"use client";

import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";
import type { Cart, Profile } from "./types";

const ACCESS = "pk_access";
const REFRESH = "pk_refresh";

export class ApiError extends Error {
  constructor(public status: number, public data: unknown) {
    super(`Request failed with ${status}`);
  }
}

function read(key: string): string | null {
  try {
    return localStorage.getItem(key);
  } catch {
    return null;
  }
}

function write(key: string, value: string | null) {
  try {
    if (value) localStorage.setItem(key, value);
    else localStorage.removeItem(key);
  } catch {
    /* storage blocked: the session just won't survive a reload */
  }
}

async function refreshAccess(): Promise<string | null> {
  const refresh = read(REFRESH);
  if (!refresh) return null;
  const res = await fetch("/api/account/token/refresh/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ refresh }),
  });
  if (!res.ok) {
    write(ACCESS, null);
    write(REFRESH, null);
    return null;
  }
  const data = await res.json();
  write(ACCESS, data.access);
  // ROTATE_REFRESH_TOKENS is on, so a new refresh token comes back too.
  if (data.refresh) write(REFRESH, data.refresh);
  return data.access;
}

// Calls the Django API through the Next proxy with the JWT attached,
// refreshing the access token once when it has expired.
export async function api<T = unknown>(path: string, init: RequestInit = {}): Promise<T> {
  const send = (token: string | null) => {
    const headers = new Headers(init.headers);
    if (token) headers.set("Authorization", `Bearer ${token}`);
    if (init.body && !(init.body instanceof FormData)) headers.set("Content-Type", "application/json");
    return fetch(`/api/${path}`, { ...init, headers });
  };

  let res = await send(read(ACCESS));
  if (res.status === 401 && read(REFRESH)) {
    const token = await refreshAccess();
    if (token) res = await send(token);
  }

  const text = await res.text();
  const data = text ? JSON.parse(text) : null;
  if (!res.ok) throw new ApiError(res.status, data);
  return data as T;
}

interface Session {
  ready: boolean;
  user: Profile | null;
  cartCount: number;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  reloadUser: () => Promise<void>;
  setCart: (cart: Cart) => void;
}

const SessionContext = createContext<Session | null>(null);

export function SessionProvider({ children }: { children: React.ReactNode }) {
  const [ready, setReady] = useState(false);
  const [user, setUser] = useState<Profile | null>(null);
  const [cartCount, setCartCount] = useState(0);

  const reloadUser = useCallback(async () => {
    if (!read(ACCESS) && !read(REFRESH)) {
      setUser(null);
      setCartCount(0);
      return;
    }
    try {
      const [profile, cart] = await Promise.all([
        api<Profile>("account/profile/"),
        api<Cart>("shop/cart/"),
      ]);
      setUser(profile);
      setCartCount(cart.total_items);
    } catch {
      write(ACCESS, null);
      write(REFRESH, null);
      setUser(null);
      setCartCount(0);
    }
  }, []);

  useEffect(() => {
    reloadUser().finally(() => setReady(true));
  }, [reloadUser]);

  const login = useCallback(
    async (email: string, password: string) => {
      const tokens = await api<{ access: string; refresh: string }>("account/token/", {
        method: "POST",
        body: JSON.stringify({ email, password }),
      });
      write(ACCESS, tokens.access);
      write(REFRESH, tokens.refresh);
      await reloadUser();
    },
    [reloadUser],
  );

  const logout = useCallback(async () => {
    const refresh = read(REFRESH);
    if (refresh) {
      // Blacklist the refresh token server-side; log out locally either way.
      await api("account/logout/", { method: "POST", body: JSON.stringify({ refresh }) }).catch(() => {});
    }
    write(ACCESS, null);
    write(REFRESH, null);
    setUser(null);
    setCartCount(0);
  }, []);

  const setCart = useCallback((cart: Cart) => setCartCount(cart.total_items), []);

  const value = useMemo(
    () => ({ ready, user, cartCount, login, logout, reloadUser, setCart }),
    [ready, user, cartCount, login, logout, reloadUser, setCart],
  );
  return <SessionContext.Provider value={value}>{children}</SessionContext.Provider>;
}

export function useSession(): Session {
  const session = useContext(SessionContext);
  if (!session) throw new Error("useSession must be used inside <SessionProvider>");
  return session;
}

export function fullName(user: Profile): string {
  return `${user.first_name} ${user.last_name}`.trim() || user.email;
}

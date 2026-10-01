"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import { useSession } from "@/lib/session";
import type { CategoryNode } from "@/lib/types";
import CategoryMenu from "./CategoryMenu";

// The cursor-tracking highlight base.html wires onto every .btn and navbar link.
function useCursorGlow() {
  useEffect(() => {
    const onMove = (e: MouseEvent) => {
      const el = (e.target as HTMLElement | null)?.closest<HTMLElement>(".btn, .navbar .nav-link");
      if (!el) return;
      const rect = el.getBoundingClientRect();
      el.style.setProperty("--mx", `${e.clientX - rect.left}px`);
      el.style.setProperty("--my", `${e.clientY - rect.top}px`);
    };
    document.addEventListener("mousemove", onMove);
    return () => document.removeEventListener("mousemove", onMove);
  }, []);
}

export default function ShopNavbar({ categories }: { categories: CategoryNode[] }) {
  const router = useRouter();
  const { user, cartCount, logout } = useSession();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const closeTimer = useRef<ReturnType<typeof setTimeout> | undefined>(undefined);

  useCursorGlow();

  const openMenu = () => {
    clearTimeout(closeTimer.current);
    setMenuOpen(true);
  };
  const closeMenuSoon = () => {
    closeTimer.current = setTimeout(() => setMenuOpen(false), 300);
  };

  const onSearch = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const q = new FormData(e.currentTarget).get("q")?.toString().trim() ?? "";
    router.push(`/search/?q=${encodeURIComponent(q)}`);
  };

  const onLogout = async () => {
    await logout();
    setSidebarOpen(false);
    router.push("/");
  };

  return (
    <>
      <nav className="navbar navbar-expand-lg navbar-dark bg-dark krait-navbar">
        <div className="container-fluid krait-navbar-row">
          <button className="btn krait-btn-dark krait-sidebar-toggle" type="button" aria-label="Menu" onClick={() => setSidebarOpen(true)}>
            <i className="fas fa-bars" />
          </button>

          {categories.length > 0 && (
            <li className="nav-item dropdown list-unstyled" onMouseEnter={openMenu} onMouseLeave={closeMenuSoon}>
              <a
                className="nav-link dropdown-toggle"
                href="#"
                role="button"
                aria-haspopup="true"
                aria-expanded={menuOpen}
                onClick={(e) => {
                  e.preventDefault();
                  setMenuOpen((open) => !open);
                }}
              >
                Categories
              </a>
              <div
                className="dropdown-menu dropdown-menu-right categories-menu"
                style={{ minWidth: 300, display: menuOpen ? "block" : undefined }}
              >
                <div className="container p-3">
                  <div className="row row-cols-2 g-2">
                    {categories.map((category) => (
                      <div className="col" key={category.id}>
                        <CategoryMenu category={category} onNavigate={() => setMenuOpen(false)} />
                      </div>
                    ))}
                  </div>
                  <hr className="my-2" />
                  <div className="text-center">
                    <Link href="/categories/" className="btn btn-outline-primary btn-sm" onClick={() => setMenuOpen(false)}>
                      <i className="fas fa-list" /> View all categories
                    </Link>
                  </div>
                </div>
              </div>
            </li>
          )}

          <form className="d-flex flex-grow-1 mx-3" onSubmit={onSearch} style={{ minWidth: 0 }}>
            <div className="input-group krait-searchbar">
              <input
                type="search"
                name="q"
                className="form-control"
                placeholder="Search products..."
                aria-label="Search"
                style={{ border: "none", background: "transparent", boxShadow: "none", outline: "none" }}
              />
              <button className="btn" type="submit" style={{ border: "none", background: "transparent", padding: 0, marginRight: "0.5rem" }}>
                <i className="fas fa-search" />
              </button>
            </div>
          </form>

          <Link className="navbar-brand mb-0 krait-brand" href="/">
            <img className="krait-logo-full" src="/images/productkrait-navbar-logo.png" alt="ProductKrait" />
            <span className="krait-logo-text">Product Krait</span>
          </Link>
        </div>
      </nav>

      <div className={`krait-sidebar-backdrop${sidebarOpen ? " show" : ""}`} onClick={() => setSidebarOpen(false)} />
      <div className={`krait-sidebar${sidebarOpen ? " show" : ""}`}>
        <button className="btn krait-btn-dark krait-sidebar-close" type="button" aria-label="Close menu" onClick={() => setSidebarOpen(false)}>
          <i className="fas fa-times" />
        </button>
        <div className="krait-sidebar-links" onClick={(e) => (e.target as HTMLElement).closest("a") && setSidebarOpen(false)}>
          {user ? (
            <>
              <Link id="cart" href="/checkout/" className="btn krait-btn-dark">
                <i className="fas fa-shopping-cart" /> <span>Cart ({cartCount})</span>
              </Link>
              {/* A full load: the account area has its own root layout (AdminLTE). */}
              <a className="btn krait-btn-dark" href="/account/profile/">My Account</a>
              <button type="button" className="btn krait-btn-dark" onClick={onLogout}>Log out</button>
            </>
          ) : (
            <>
              <a className="btn krait-btn-dark" href="/account/login/">Log in</a>
              <a className="btn krait-btn-dark" href="/account/signup/">Sign up</a>
            </>
          )}
        </div>
      </div>
    </>
  );
}

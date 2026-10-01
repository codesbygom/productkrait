"use client";

import { useState } from "react";
import { api, ApiError, useSession } from "@/lib/session";
import { errorMessages } from "@/lib/format";
import type { Cart } from "@/lib/types";

interface Props {
  productId: number;
  quantity?: number;
  className: string;
  disabled?: boolean;
  children: React.ReactNode;
}

// Replaces the POST form to shop:add_to_cart. Guests go to the login page
// first, like the login_required Django view.
export default function AddToCartButton({ productId, quantity = 1, className, disabled, children }: Props) {
  const { user, ready, setCart } = useSession();
  const [busy, setBusy] = useState(false);
  const [done, setDone] = useState(false);

  const add = async () => {
    if (ready && !user) {
      window.location.href = `/account/login/?next=${encodeURIComponent(window.location.pathname)}`;
      return;
    }
    setBusy(true);
    try {
      const cart = await api<Cart>("shop/cart/items/", {
        method: "POST",
        body: JSON.stringify({ product_id: productId, quantity }),
      });
      setCart(cart);
      setDone(true);
      setTimeout(() => setDone(false), 1500);
    } catch (e) {
      alert(e instanceof ApiError ? errorMessages(e.data).join("\n") : "Could not add to cart.");
    } finally {
      setBusy(false);
    }
  };

  return (
    <button type="button" className={className} disabled={disabled || busy} onClick={add}>
      {done ? (
        <>
          <i className="fas fa-check" /> Added
        </>
      ) : (
        children
      )}
    </button>
  );
}

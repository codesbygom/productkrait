"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { errorMessages, mediaUrl, toman } from "@/lib/format";
import { api, ApiError, fullName, useSession } from "@/lib/session";
import type { Cart } from "@/lib/types";

const BACKEND = process.env.NEXT_PUBLIC_BACKEND_URL ?? "http://127.0.0.1:8000";

// templates/shop/checkout.html
export default function CheckoutPage() {
  const { ready, user, setCart } = useSession();
  const [cart, setCartState] = useState<Cart | null>(null);
  const [quantities, setQuantities] = useState<Record<number, number>>({});
  const [message, setMessage] = useState<{ kind: "success" | "danger"; text: string } | null>(null);
  const [shipping, setShipping] = useState({ full_name: "", phone: "", address: "" });

  const applyCart = (next: Cart) => {
    setCartState(next);
    setCart(next);
    setQuantities(Object.fromEntries(next.items.map((item) => [item.product.id, item.quantity])));
  };

  useEffect(() => {
    if (!ready) return;
    if (!user) {
      window.location.href = "/account/login/?next=/checkout/";
      return;
    }
    setShipping({
      full_name: fullName(user) === user.email ? "" : fullName(user),
      phone: user.phone?.toString() ?? "",
      address: [user.city, user.address, user.zipcode].filter(Boolean).join(", "),
    });
    api<Cart>("shop/cart/").then(applyCart).catch(() => setMessage({ kind: "danger", text: "Could not load your cart." }));
  }, [ready, user]);

  const run = async (request: Promise<Cart>, success: string) => {
    try {
      applyCart(await request);
      setMessage({ kind: "success", text: success });
    } catch (e) {
      setMessage({ kind: "danger", text: e instanceof ApiError ? errorMessages(e.data).join(" ") : "Something went wrong." });
    }
  };

  const update = (productId: number) =>
    run(
      api<Cart>(`shop/cart/items/${productId}/`, { method: "PATCH", body: JSON.stringify({ quantity: quantities[productId] }) }),
      "Cart updated.",
    );

  const remove = (productId: number) => {
    if (!confirm("Are you sure you want to remove this product from your cart?")) return;
    run(api<Cart>(`shop/cart/items/${productId}/`, { method: "DELETE" }), "Product removed from your cart.");
  };

  // Payment runs through the bank gateway in the Django app (it needs the
  // Django session), so the order is placed on the Django checkout page.
  const proceed = (e: React.FormEvent) => {
    e.preventDefault();
    window.location.href = `${BACKEND}/checkout/`;
  };

  if (!cart) {
    return (
      <div className="checkout-container text-center py-5">
        <link rel="stylesheet" href="/static/shop/checkout.css" />
        {message ? <div className={`alert alert-${message.kind}`}>{message.text}</div> : <i className="fas fa-spinner fa-spin fa-2x" />}
      </div>
    );
  }

  return (
    <div className="checkout-container">
      <link rel="stylesheet" href="/static/shop/checkout.css" />
      <link rel="stylesheet" href="/static/shop/checkout-page.css" />
      {message && <div className={`alert alert-${message.kind}`}>{message.text}</div>}

      {cart.items.length === 0 ? (
        <div className="empty-cart-message">
          <i className="fas fa-shopping-cart" />
          <h3 className="mb-2">Your cart is empty</h3>
          <p className="text-muted mb-3">Visit the ProductKrait page to browse products and add them to your cart.</p>
          <Link href="/" className="btn btn-primary btn-sm">
            Browse Products
          </Link>
        </div>
      ) : (
        <div className="row">
          <div className="col-md-8">
            <div className="card">
              <div className="card-header">
                <h5>Cart</h5>
              </div>
              <div className="card-body p-0">
                <div className="table-responsive">
                  <table className="table table-sm mb-0">
                    <thead>
                      <tr>
                        <th style={{ width: 50 }}>Image</th>
                        <th>Product Name</th>
                        <th style={{ width: 90 }}>Price</th>
                        <th style={{ width: 120 }}>Quantity</th>
                        <th style={{ width: 50 }}>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {cart.items.map((item) => (
                        <tr key={item.id}>
                          <td>
                            <img src={mediaUrl(item.product.image)} className="product-image" alt={item.product.title} />
                          </td>
                          <td>
                            <Link href={`/product/${item.product.id}/`} className="product-title">
                              {item.product.title}
                            </Link>
                          </td>
                          <td className="product-price">{toman(item.product.price)}</td>
                          <td>
                            <div className="d-flex align-items-center">
                              <input
                                type="number"
                                className="form-control form-control-sm quantity-input"
                                value={quantities[item.product.id] ?? item.quantity}
                                min={1}
                                onChange={(e) =>
                                  setQuantities((q) => ({ ...q, [item.product.id]: Math.max(1, Number(e.target.value) || 1) }))
                                }
                              />
                              <button type="button" className="btn btn-sm btn-success ms-2" onClick={() => update(item.product.id)}>
                                <i className="fas fa-sync-alt" />
                              </button>
                            </div>
                          </td>
                          <td>
                            <button type="button" className="btn btn-sm btn-danger" onClick={() => remove(item.product.id)}>
                              <i className="fas fa-trash" />
                            </button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>

            <div className="card">
              <div className="card-header">
                <h5>Shipping Information</h5>
              </div>
              <div className="card-body">
                <form id="checkout-form" onSubmit={proceed}>
                  <div className="row g-2">
                    <div className="col-md-6">
                      <label htmlFor="full_name" className="form-label">Full Name</label>
                      <input
                        type="text"
                        className="form-control form-control-sm"
                        id="full_name"
                        value={shipping.full_name}
                        onChange={(e) => setShipping({ ...shipping, full_name: e.target.value })}
                        required
                      />
                    </div>
                    <div className="col-md-6">
                      <label htmlFor="phone" className="form-label">Phone Number</label>
                      <input
                        type="tel"
                        className="form-control form-control-sm"
                        id="phone"
                        inputMode="numeric"
                        pattern="[0-9]*"
                        value={shipping.phone}
                        onChange={(e) => setShipping({ ...shipping, phone: e.target.value.replace(/[^0-9]/g, "") })}
                        required
                      />
                    </div>
                    <div className="col-12">
                      <label htmlFor="address" className="form-label">Full Address</label>
                      <textarea
                        className="form-control form-control-sm"
                        id="address"
                        rows={2}
                        value={shipping.address}
                        onChange={(e) => setShipping({ ...shipping, address: e.target.value })}
                        required
                      />
                    </div>
                  </div>
                </form>
              </div>
            </div>
          </div>

          <div className="col-md-4">
            <div className="card">
              <div className="card-header">
                <h5>Order Summary</h5>
              </div>
              <div className="card-body">
                <div className="checkout-summary">
                  <div className="checkout-summary-item">
                    <span>Number of products:</span>
                    <span>{cart.items.length}</span>
                  </div>
                  <div className="checkout-summary-item">
                    <span>Subtotal:</span>
                    <span className="total-price">{toman(cart.total_price)}</span>
                  </div>
                  <div className="checkout-summary-item">
                    <span>Shipping cost:</span>
                    <span>Free</span>
                  </div>
                  <div className="checkout-summary-total">
                    <span>Total due:</span>
                    <span>{toman(cart.total_price)}</span>
                  </div>
                </div>

                <button type="submit" form="checkout-form" className="btn btn-primary w-100 mt-2">
                  <i className="fas fa-credit-card" /> Proceed to Payment
                </button>

                <Link href="/" className="btn btn-outline-secondary w-100 mt-2">
                  <i className="fas fa-arrow-left" /> Back to ProductKrait
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

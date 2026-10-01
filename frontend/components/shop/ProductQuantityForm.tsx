"use client";

import Link from "next/link";
import { useState } from "react";
import AddToCartButton from "./AddToCartButton";

// The quantity + add-to-cart form on the product detail page.
export default function ProductQuantityForm({ productId, stock }: { productId: number; stock: number }) {
  const [quantity, setQuantity] = useState(1);
  const outOfStock = stock === 0;

  return (
    <div className="mt-3">
      <div className="form-group">
        <label htmlFor="quantity">Quantity:</label>
        <input
          type="number"
          className="form-control quantity-input"
          id="quantity"
          value={quantity}
          min={1}
          max={stock}
          disabled={outOfStock}
          onChange={(e) => setQuantity(Math.max(1, Math.min(stock, Number(e.target.value) || 1)))}
          style={{ width: 100 }}
        />
      </div>

      <div className="detail-buttons">
        <Link href="/" className="btn btn-outline-secondary">
          <i className="fas fa-arrow-left" /> Back to ProductKrait
        </Link>
        <AddToCartButton productId={productId} quantity={quantity} className="btn btn-add-to-cart" disabled={outOfStock}>
          <i className="fas fa-shopping-cart" /> {outOfStock ? "Out of Stock" : "Add to Cart"}
        </AddToCartButton>
      </div>
    </div>
  );
}

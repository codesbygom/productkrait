import Link from "next/link";
import { mediaUrl, truncate } from "@/lib/format";
import type { Product } from "@/lib/types";
import AddToCartButton from "./AddToCartButton";

// The product card shared by index.html, category.html and search.html.
// `withDescription` matches the category/search variant.
export default function ProductCard({ product, withDescription = false }: { product: Product; withDescription?: boolean }) {
  return (
    <div className={withDescription ? "card h-100" : "card"}>
      <img src={mediaUrl(product.image)} className="card-img-top" alt={product.image ? product.title : "No image"} />
      <div className="card-body">
        {withDescription ? (
          <>
            <h5 className="card-title">{product.title}</h5>
            <div className="card-text">{truncate(product.description, 100)}</div>
          </>
        ) : (
          <div className="card-title">
            <Link href={`/product/${product.id}/`}>{product.title}</Link>
          </div>
        )}
        <p className="card-text">
          <strong>Price:</strong> {product.price} Toman
        </p>
        <div className="d-flex justify-content-between align-items-center">
          {product.quantity > 0 ? (
            <AddToCartButton productId={product.id} className="btn btn-primary btn-sm">
              <i className="fas fa-cart-plus" /> Add to Cart
            </AddToCartButton>
          ) : (
            <button className="btn btn-secondary btn-sm" disabled>
              <i className="fas fa-times-circle" /> Out of Stock
            </button>
          )}
          <Link href={`/product/${product.id}/`} className="btn btn-outline-primary btn-sm">
            <i className="fas fa-eye" /> View
          </Link>
        </div>
      </div>
    </div>
  );
}

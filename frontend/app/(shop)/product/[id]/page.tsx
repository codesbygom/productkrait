import type { Metadata } from "next";
import ProductQuantityForm from "@/components/shop/ProductQuantityForm";
import { mediaUrl, toman } from "@/lib/format";
import { getProduct } from "@/lib/server-api";

type Props = { params: Promise<{ id: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const product = await getProduct((await params).id);
  return { title: product.title };
}

// templates/shop/detail.html
export default async function ProductDetailPage({ params }: Props) {
  const product = await getProduct((await params).id);
  const inStock = product.quantity > 0;

  return (
    <>
      <link rel="stylesheet" href="/static/shop/detail.css" />
      <div className="row">
        <div className="col-md-12">
          <div className="product-detail">
            <div className="row">
              <div className="col-md-6">
                <img src={mediaUrl(product.image)} className="product-image" alt={product.image ? product.title : "No image"} />
              </div>
              <div className="col-md-6">
                <h1 className="product-title">{product.title}</h1>
                <div className="product-price">{toman(product.price)}</div>
                {/* Staff-authored rich text, rendered unescaped like |safe in the template. */}
                <div className="product-description" dangerouslySetInnerHTML={{ __html: product.description }} />

                <div className="stock-info mb-3">
                  {inStock ? (
                    <span className="text-success">
                      <i className="fas fa-check-circle" /> In stock: {product.quantity}
                    </span>
                  ) : (
                    <span className="text-danger">
                      <i className="fas fa-times-circle" /> Out of Stock
                    </span>
                  )}
                </div>

                <ProductQuantityForm productId={product.id} stock={product.quantity} />
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

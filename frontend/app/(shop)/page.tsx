import Pagination, { pageNumber } from "@/components/shop/Pagination";
import ProductCard from "@/components/shop/ProductCard";
import { getProducts } from "@/lib/server-api";

// templates/shop/index.html
export default async function IndexPage({ searchParams }: { searchParams: Promise<{ page?: string }> }) {
  const page = pageNumber((await searchParams).page);
  const products = await getProducts({ page: String(page) });

  return (
    <>
      <link rel="stylesheet" href="/static/shop/index.css" />
      <div className="row">
        {products.results.length > 0 ? (
          products.results.map((product) => (
            <div className="col-md-3" key={product.id}>
              <ProductCard product={product} />
            </div>
          ))
        ) : (
          <div className="col-12 text-center">
            <h3>No products found</h3>
          </div>
        )}
      </div>
      <Pagination count={products.count} page={page} href={(n) => `/?page=${n}`} />
    </>
  );
}

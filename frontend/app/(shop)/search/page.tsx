import type { Metadata } from "next";
import Pagination, { pageNumber } from "@/components/shop/Pagination";
import ProductCard from "@/components/shop/ProductCard";
import { getProducts } from "@/lib/server-api";

type Props = { searchParams: Promise<{ q?: string; page?: string }> };

export async function generateMetadata({ searchParams }: Props): Promise<Metadata> {
  return { title: `Search results for "${(await searchParams).q ?? ""}" - ProductKrait` };
}

// templates/shop/search.html
export default async function SearchPage({ searchParams }: Props) {
  const params = await searchParams;
  const query = params.q?.trim() ?? "";
  const page = pageNumber(params.page);
  const products = query
    ? await getProducts({ search: query, page: String(page) })
    : { count: 0, next: null, previous: null, results: [] };

  return (
    <>
      <link rel="stylesheet" href="/static/shop/category.css" />
      <div className="category-header">
        <div className="container text-center">
          <h1 className="category-title">Search results for &quot;{query}&quot;</h1>
          <p className="text-muted">Number of results: {products.count}</p>
        </div>
      </div>

      <div className="container">
        <div className="row">
          {products.results.length > 0 ? (
            products.results.map((product) => (
              <div className="col-md-6 col-lg-4 col-xl-3 mb-4" key={product.id}>
                <ProductCard product={product} withDescription />
              </div>
            ))
          ) : (
            <div className="col-12">
              <div className="alert alert-info text-center">
                <i className="fas fa-search fa-3x mb-3" />
                <h4>No results found</h4>
                <p>Unfortunately, no products were found matching &quot;{query}&quot;.</p>
                <p>Please try a different search term or browse the available categories.</p>
              </div>
            </div>
          )}
        </div>
        <Pagination
          count={products.count}
          page={page}
          href={(n) => `/search/?q=${encodeURIComponent(query)}&page=${n}`}
        />
      </div>
    </>
  );
}

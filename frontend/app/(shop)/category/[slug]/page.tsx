import type { Metadata } from "next";
import Pagination, { pageNumber } from "@/components/shop/Pagination";
import ProductCard from "@/components/shop/ProductCard";
import { getCategory, getProducts } from "@/lib/server-api";

type Props = { params: Promise<{ slug: string }>; searchParams: Promise<{ page?: string }> };

export async function generateMetadata({ params }: Props): Promise<Metadata> {
  const category = await getCategory((await params).slug);
  return { title: `${category.title} - ProductKrait` };
}

// templates/shop/category.html
export default async function CategoryPage({ params, searchParams }: Props) {
  const { slug } = await params;
  const page = pageNumber((await searchParams).page);
  const [category, products] = await Promise.all([
    getCategory(slug),
    getProducts({ category: slug, page: String(page) }),
  ]);

  return (
    <>
      <link rel="stylesheet" href="/static/shop/category.css" />
      <div className="category-header">
        <div className="container text-center">
          <h1 className="category-title">{category.title}</h1>
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
              <div className="alert alert-info">No products found in this category.</div>
            </div>
          )}
        </div>
        <Pagination count={products.count} page={page} href={(n) => `/category/${slug}/?page=${n}`} />
      </div>
    </>
  );
}

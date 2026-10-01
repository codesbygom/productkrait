import type { Metadata } from "next";
import Link from "next/link";
import { getCategoryTree } from "@/lib/server-api";
import type { CategoryNode } from "@/lib/types";

export const metadata: Metadata = { title: "Categories - ProductKrait" };

// templates/shop/vertical_category_menu.html
function VerticalCategory({ category }: { category: CategoryNode }) {
  const hasChildren = category.children.length > 0;
  return (
    <div className="vertical-category-item">
      <Link className="vertical-category-link" href={`/category/${category.slug}/`}>
        <i className={`fas ${hasChildren ? "fa-folder" : "fa-tag"}`} /> {category.title}
        {hasChildren && <i className="fas fa-chevron-right float-right" />}
      </Link>
      {hasChildren && (
        <div className="vertical-submenu">
          {category.children.map((child) => (
            <VerticalCategory key={child.id} category={child} />
          ))}
        </div>
      )}
    </div>
  );
}

// templates/shop/categories_page.html
export default async function CategoriesPage() {
  const categories = await getCategoryTree();

  return (
    <>
      <link rel="stylesheet" href="/static/shop/category.css" />
      <link rel="stylesheet" href="/static/shop/categories-page.css" />
      <div className="categories-container">
        <div className="categories-header">
          <h1>Product Categories</h1>
          <p>All categories and subcategories of ProductKrait</p>
        </div>

        <div className="row">
          <div className="col-12">
            {categories.length > 0 ? (
              categories.map((category) => <VerticalCategory key={category.id} category={category} />)
            ) : (
              <div className="alert alert-info text-center">
                <i className="fas fa-info-circle" /> No categories found.
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}

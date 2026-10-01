import { notFound } from "next/navigation";
import type { CategoryDetail, CategoryListItem, CategoryNode, Paginated, Product } from "./types";

const BACKEND = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

// Public catalogue reads, done on the server so product pages render with
// their content (the same data the Django views put in the templates).
async function get<T>(path: string): Promise<T> {
  const res = await fetch(`${BACKEND}/api/shop/${path}`, { cache: "no-store" });
  if (res.status === 404) notFound();
  if (!res.ok) throw new Error(`GET ${path} failed with ${res.status}`);
  return res.json() as Promise<T>;
}

export function getProducts(params: Record<string, string | undefined>) {
  const query = new URLSearchParams();
  for (const [key, value] of Object.entries(params)) if (value) query.set(key, value);
  return get<Paginated<Product>>(`products/?${query}`);
}

export const getProduct = (id: string) => get<Product>(`products/${encodeURIComponent(id)}/`);

export const getCategory = (slug: string) => get<CategoryDetail>(`category/${encodeURIComponent(slug)}/`);

// Builds the same parent -> children tree the category_tags template tag
// gives the Django templates.
export async function getCategoryTree(): Promise<CategoryNode[]> {
  let flat: CategoryListItem[];
  try {
    flat = await get<CategoryListItem[]>("category/");
  } catch {
    return [];
  }
  const nodes = new Map<number, CategoryNode>(flat.map((c) => [c.id, { ...c, children: [] }]));
  const roots: CategoryNode[] = [];
  for (const node of nodes.values()) {
    const parent = node.parent != null ? nodes.get(node.parent) : undefined;
    (parent ? parent.children : roots).push(node);
  }
  return roots;
}

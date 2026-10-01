// Shapes of the DRF serializers in api/api_shop and api/api_account.

export interface Paginated<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface Product {
  id: number;
  title: string;
  slug: string;
  url: string;
  description: string;
  price: string;
  discount_price: string | null;
  quantity: number;
  image: string | null;
  thumbnail: string | null;
}

export interface CategoryListItem {
  id: number;
  title: string;
  slug: string;
  parent: number | null;
  position: number;
}

export interface CategoryNode extends CategoryListItem {
  children: CategoryNode[];
}

export interface CategoryDetail {
  id: number;
  title: string;
  slug: string;
  parent: number | null;
  children: CategoryListItem[];
  products: Product[];
}

export interface CartProduct {
  id: number;
  title: string;
  slug: string;
  price: string;
  quantity: number;
  image: string | null;
}

export interface CartItem {
  id: number;
  product: CartProduct;
  quantity: number;
  price: string;
  total_price: string;
}

export interface Cart {
  id: number;
  items: CartItem[];
  total_items: number;
  total_price: string;
  updated_at: string;
}

export type OrderStatus = "pending" | "processing" | "shipped" | "delivered" | "cancelled";

export interface Order {
  id: number;
  tracking_number: string | null;
  status: OrderStatus;
  status_display: string;
  total_price: string;
  shipping_address: string;
  tracking_code: string | null;
  items: CartItem[];
  created_at: string;
  updated_at: string;
}

export interface Profile {
  id: number;
  email: string;
  username: string;
  first_name: string;
  last_name: string;
  zipcode: number | null;
  address: string | null;
  city: string | null;
  phone: number | null;
  is_email_verified: boolean;
}

import type { OrderStatus } from "@/lib/types";

const BADGES: Record<OrderStatus, [string, string]> = {
  pending: ["badge-warning", "Awaiting payment"],
  processing: ["badge-info", "Processing"],
  shipped: ["badge-primary", "Shipped"],
  delivered: ["badge-success", "Delivered"],
  cancelled: ["badge-danger", "Cancelled"],
};

export default function OrderStatusBadge({ status }: { status: OrderStatus }) {
  const badge = BADGES[status];
  return badge ? <span className={`badge ${badge[0]}`}>{badge[1]}</span> : null;
}

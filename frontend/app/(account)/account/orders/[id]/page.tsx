"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { useEffect, useState } from "react";
import { AccountPage } from "@/components/account/AccountShell";
import OrderStatusBadge from "@/components/account/OrderStatusBadge";
import { formatDate, mediaUrl, toman } from "@/lib/format";
import { api } from "@/lib/session";
import type { Order } from "@/lib/types";

// templates/Account/order_detail.html
export default function OrderDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [order, setOrder] = useState<Order | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    api<Order>(`shop/orders/${id}/`).then(setOrder).catch(() => setFailed(true));
  }, [id]);

  if (failed) {
    return (
      <AccountPage title="Order not found">
        <div className="alert alert-danger">This order does not exist or does not belong to you.</div>
        <Link href="/account/orders/" className="btn btn-secondary">
          <i className="fas fa-arrow-left" /> Back to Order List
        </Link>
      </AccountPage>
    );
  }
  if (!order) return <AccountPage title={`Order Details #${id}`}><i className="fas fa-spinner fa-spin" /></AccountPage>;

  const totalItems = order.items.reduce((sum, item) => sum + item.quantity, 0);

  return (
    <AccountPage title={`Order Details #${order.id}`}>
      <link rel="stylesheet" href="/static/account/order-detail.css" />
      <div className="row">
        <div className="col-md-8 mx-auto">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">Order Info #{order.id}</h3>
            </div>
            <div className="card-body">
              <div className="row">
                <div className="col-md-6">
                  <p><strong>Placed at:</strong> {formatDate(order.created_at)}</p>
                  <p><strong>Last updated:</strong> {formatDate(order.updated_at)}</p>
                  <p><strong>Total:</strong> {toman(order.total_price, 2)}</p>
                </div>
                <div className="col-md-6">
                  <p><strong>Order status:</strong> <OrderStatusBadge status={order.status} /></p>
                  {order.tracking_number && (
                    <p><strong>Tracking number:</strong> <span className="badge badge-primary">{order.tracking_number}</span></p>
                  )}
                  <p>
                    <strong>Shipping tracking code:</strong>{" "}
                    {order.tracking_code ? (
                      <span className="badge badge-info">{order.tracking_code}</span>
                    ) : (
                      <span className="text-muted">Not recorded</span>
                    )}
                  </p>
                  <p><strong>Total items:</strong> {totalItems}</p>
                </div>
              </div>
              <div className="row mt-3">
                <div className="col-12">
                  <p><strong>Shipping address:</strong></p>
                  <div className="alert alert-info">{order.shipping_address}</div>
                </div>
              </div>
            </div>
          </div>

          <div className="card mt-4">
            <div className="card-header">
              <h3 className="card-title">Order Items</h3>
            </div>
            <div className="card-body p-0">
              <div className="table-responsive">
                <table className="table table-striped">
                  <thead>
                    <tr>
                      <th>Image</th>
                      <th>Product Name</th>
                      <th>Unit Price</th>
                      <th>Quantity</th>
                      <th>Total Price</th>
                    </tr>
                  </thead>
                  <tbody>
                    {order.items.map((item) => (
                      <tr key={item.id}>
                        <td>
                          {item.product.image ? (
                            <img src={mediaUrl(item.product.image)} alt={item.product.title} style={{ width: 50, height: 50, objectFit: "cover" }} />
                          ) : (
                            <div className="bg-light text-center" style={{ width: 50, height: 50, lineHeight: "50px" }}>
                              <i className="fas fa-image text-muted" />
                            </div>
                          )}
                        </td>
                        <td>
                          <a href={`/product/${item.product.id}/`} target="_blank">{item.product.title}</a>
                        </td>
                        <td>{toman(item.price, 2)}</td>
                        <td>{item.quantity}</td>
                        <td>{toman(item.total_price, 2)}</td>
                      </tr>
                    ))}
                  </tbody>
                  <tfoot>
                    <tr>
                      <td colSpan={4} className="text-left"><strong>Grand Total:</strong></td>
                      <td><strong>{toman(order.total_price, 2)}</strong></td>
                    </tr>
                  </tfoot>
                </table>
              </div>
            </div>
          </div>

          <div className="text-center mt-4">
            <Link href="/account/orders/" className="btn btn-secondary">
              <i className="fas fa-arrow-left" /> Back to Order List
            </Link>
          </div>
        </div>
      </div>
    </AccountPage>
  );
}

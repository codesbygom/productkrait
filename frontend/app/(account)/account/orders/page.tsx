"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { AccountPage } from "@/components/account/AccountShell";
import OrderStatusBadge from "@/components/account/OrderStatusBadge";
import { formatDate, toman } from "@/lib/format";
import { api } from "@/lib/session";
import type { Order, Paginated } from "@/lib/types";

// templates/Account/orders.html
export default function OrdersPage() {
  const [orders, setOrders] = useState<Order[] | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    api<Paginated<Order>>("shop/orders/")
      .then((page) => setOrders(page.results))
      .catch(() => setFailed(true));
  }, []);

  return (
    <AccountPage title="My Orders">
      <div className="row">
        <div className="col-12">
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">My Orders</h3>
            </div>
            <div className="card-body">
              {failed && <div className="alert alert-danger">Could not load your orders.</div>}
              {!orders && !failed && <i className="fas fa-spinner fa-spin" />}
              {orders && orders.length > 0 && (
                <div className="table-responsive">
                  <table className="table table-bordered table-striped">
                    <thead>
                      <tr>
                        <th>Order Number</th>
                        <th>Placed At</th>
                        <th>Status</th>
                        <th>Total</th>
                        <th>Actions</th>
                      </tr>
                    </thead>
                    <tbody>
                      {orders.map((order) => (
                        <tr key={order.id}>
                          <td>#{order.id}</td>
                          <td>{formatDate(order.created_at)}</td>
                          <td><OrderStatusBadge status={order.status} /></td>
                          <td>{toman(order.total_price, 2)}</td>
                          <td>
                            <Link href={`/account/orders/${order.id}/`} className="btn btn-info btn-sm">
                              <i className="fas fa-eye" /> View
                            </Link>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
              {orders && orders.length === 0 && (
                <div className="alert alert-info text-center">
                  <i className="fas fa-info-circle fa-2x mb-3" />
                  <h4>You haven&apos;t placed any orders yet</h4>
                  <p className="mt-3">
                    Visit <a href="/" className="alert-link">ProductKrait</a> to place a new order
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </AccountPage>
  );
}

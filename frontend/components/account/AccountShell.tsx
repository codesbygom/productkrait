"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useEffect } from "react";
import { fullName, useSession } from "@/lib/session";

const MENU = [
  { href: "/account/orders/", icon: "fas fa-shopping-cart", label: "Order History" },
  { href: "/account/profile/", icon: "far fa-user", label: "Edit Profile" },
  { href: "/account/password/", icon: "fas fa-key", label: "Change Password" },
];

// AdminLTE's pushmenu: collapses to an icon rail on desktop, slides the
// sidebar in and out below 992px.
function togglePushMenu() {
  const body = document.body.classList;
  if (window.innerWidth >= 992) body.toggle("sidebar-collapse");
  else body.toggle("sidebar-open");
}

// Navbar + sidebar of templates/Account/base.html and sidebar.html. Every
// page here needs a signed-in user, like the LoginRequiredMixin views.
export default function AccountShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const { ready, user, logout } = useSession();

  useEffect(() => {
    if (ready && !user) window.location.href = `/account/login/?next=${encodeURIComponent(pathname)}`;
  }, [ready, user, pathname]);

  useEffect(() => {
    document.body.classList.remove("sidebar-open");
  }, [pathname]);

  const onLogout = async () => {
    await logout();
    window.location.href = "/";
  };

  return (
    <div className="wrapper">
      <nav className="main-header navbar navbar-expand navbar-dark krait-admin-navbar">
        <ul className="navbar-nav">
          <li className="nav-item">
            <a
              className="nav-link"
              href="#"
              role="button"
              onClick={(e) => {
                e.preventDefault();
                togglePushMenu();
              }}
            >
              <i className="fas fa-bars" />
            </a>
          </li>
          <li className="nav-item d-none d-sm-inline-block">
            <Link href="/account/profile/" className="nav-link">Home</Link>
          </li>
          <li className="nav-item d-none d-sm-inline-block">
            <a href="/" target="_blank" className="nav-link">View Site</a>
          </li>
          <li className="nav-item d-none d-sm-inline-block">
            <Link href="/account/orders/" className="nav-link">Order History</Link>
          </li>
        </ul>
        <ul className="navbar-nav ml-auto align-items-center">
          <li className="nav-item">
            <a href="/" className="nav-link py-0">
              <img src="/images/productkrait-navbar-logo.png" alt="ProductKrait" style={{ height: 40, width: "auto" }} />
            </a>
          </li>
        </ul>
      </nav>

      <aside className="main-sidebar sidebar-dark-primary elevation-4">
        <div className="sidebar krait-sidebar-flex">
          <div className="user-panel mt-3 pb-3 mb-3 d-flex">
            <div className="image">
              <i className="fas fa-user-circle fa-2x text-light" />
            </div>
            <div className="info">
              <Link href="/account/profile/" className="d-block">{user ? fullName(user) : ""}</Link>
            </div>
          </div>

          <nav className="mt-2">
            <ul className="nav nav-pills nav-sidebar flex-column" role="menu">
              {MENU.map((item) => (
                <li className="nav-item" key={item.href}>
                  <Link href={item.href} className={`nav-link${pathname.startsWith(item.href) ? " active bg-info" : ""}`}>
                    <i className={`nav-icon ${item.icon}`} />
                    <p>{item.label}</p>
                  </Link>
                </li>
              ))}
              <li className="nav-item">
                {/* The cart lives in the shop layout, so this is a full page load. */}
                <a href="/checkout/" className="nav-link">
                  <i className="nav-icon fas fa-shopping-basket" />
                  <p>View My Cart</p>
                </a>
              </li>
            </ul>
          </nav>
        </div>

        <div className="krait-sidebar-logout">
          <button type="button" className="nav-link" onClick={onLogout}>
            <i className="nav-icon fas fa-sign-out-alt" />
            <p>Log out</p>
          </button>
        </div>
      </aside>

      <div className="sidebar-overlay" onClick={() => document.body.classList.remove("sidebar-open")} />

      {/* AdminLTE's JS normally sizes this; without it, fill the viewport below the navbar. */}
      <div className="content-wrapper" style={{ minHeight: "calc(100vh - 57px)" }}>
        {user ? children : <div className="p-5 text-center"><i className="fas fa-spinner fa-spin fa-2x" /></div>}
      </div>
    </div>
  );
}

// The content-header block + <section class="content"> every account page has.
export function AccountPage({ title, children }: { title: string; children: React.ReactNode }) {
  useEffect(() => {
    document.title = title;
  }, [title]);

  return (
    <>
      <div className="content-header">
        <div className="container-fluid">
          <div className="row mb-2">
            <div className="col-sm-6">
              <h1 className="m-0 text-dark">{title}</h1>
            </div>
          </div>
        </div>
      </div>
      <section className="content">
        <div className="container-fluid">{children}</div>
      </section>
    </>
  );
}

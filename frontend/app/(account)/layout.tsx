import type { Metadata } from "next";
import AccountShell from "@/components/account/AccountShell";
import { SessionProvider } from "@/lib/session";

export const metadata: Metadata = {
  title: "Admin Panel",
  icons: { icon: "/images/productkrait-favicon-1x1.png" },
};

// templates/Account/base.html: AdminLTE with the krait black/cream palette.
export default function AccountLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" dir="ltr">
      <head>
        <meta name="color-scheme" content="light" />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/admin-lte@3.2.0/dist/css/adminlte.min.css" />
        <link href="https://fonts.googleapis.com/css?family=Source+Sans+Pro:300,400,400i,700" rel="stylesheet" />
        <link rel="stylesheet" href="/static/account/account.css" />
      </head>
      <body className="hold-transition sidebar-mini layout-fixed">
        <SessionProvider>
          <AccountShell>{children}</AccountShell>
        </SessionProvider>
      </body>
    </html>
  );
}

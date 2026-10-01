import type { Metadata } from "next";
import ShopNavbar from "@/components/shop/ShopNavbar";
import { getCategoryTree } from "@/lib/server-api";
import { SessionProvider } from "@/lib/session";

export const metadata: Metadata = {
  title: "ProductKrait",
  icons: { icon: "/images/productkrait-favicon-1x1.png" },
};

// templates/shop/base.html
export default async function ShopLayout({ children }: { children: React.ReactNode }) {
  const categories = await getCategoryTree();

  return (
    <html lang="en" dir="ltr">
      <head>
        <meta name="color-scheme" content="light" />
        <link
          rel="stylesheet"
          href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css"
          integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T"
          crossOrigin="anonymous"
        />
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css" />
        <link rel="stylesheet" href="/static/shop/style.css" />
      </head>
      <body>
        <SessionProvider>
          <ShopNavbar categories={categories} />
          <div className="container mt-3">{children}</div>
        </SessionProvider>
      </body>
    </html>
  );
}

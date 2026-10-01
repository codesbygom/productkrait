import type { Metadata } from "next";
import { SessionProvider } from "@/lib/session";

export const metadata: Metadata = {
  title: { template: "%s · ProductKrait", default: "Account · ProductKrait" },
  icons: { icon: "/images/productkrait-favicon-1x1.png" },
};

// templates/Account/auth_base.html (login, signup and password reset pages)
export default function AuthLayout({ children }: { children: React.ReactNode }) {
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
        <link rel="stylesheet" href="/static/login/util.css" />
        <link rel="stylesheet" href="/static/login/main.css" />
        <link rel="stylesheet" href="/static/login/krait-theme.css" />
      </head>
      <body>
        <SessionProvider>
          <div className="limiter">
            <div className="container-login100">
              <div className="wrap-login100">{children}</div>
            </div>
          </div>
        </SessionProvider>
      </body>
    </html>
  );
}

import type { NextConfig } from "next";

const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  // Django routes all end in a slash; keep them so DRF doesn't redirect.
  trailingSlash: true,
  // The browser only ever talks to Next; API calls and uploaded images are
  // proxied to Django, so the backend needs no CORS setup.
  async rewrites() {
    return [
      { source: "/api/:path*", destination: `${backend}/api/:path*/` },
      { source: "/media/:path*", destination: `${backend}/media/:path*` },
    ];
  },
};

export default nextConfig;

/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  // Keep trailing slashes intact so `/health/` proxies straight through to
  // the FastAPI route instead of being redirected to the slashless path.
  skipTrailingSlashRedirect: true,
  async rewrites() {
    // Server-side proxy target. The browser always calls relative `/api/*`
    // and `/health/*` (so NEXT_PUBLIC_API_URL stays ""); Next rewrites them to
    // the backend service inside the cluster. Overridable via BACKEND_URL.
    const backend = process.env.BACKEND_URL || "http://dclaw-risk-backend:18162";
    return [
      {
        source: "/api/:path*",
        destination: `${backend}/api/:path*`,
      },
      {
        source: "/health/:path*",
        destination: `${backend}/health/:path*`,
      },
    ];
  },
}

module.exports = nextConfig

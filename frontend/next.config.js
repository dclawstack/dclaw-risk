/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'standalone',
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://dclaw-risk-backend:8136/:path*',
      },
    ];
  },
};

module.exports = nextConfig;

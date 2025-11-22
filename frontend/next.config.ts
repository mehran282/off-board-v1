import type { NextConfig } from 'next';
import createNextIntlPlugin from 'next-intl/plugin';

const withNextIntl = createNextIntlPlugin('./i18n.ts');

const nextConfig: NextConfig = {
  // Enable standalone output for Docker
  output: 'standalone',
  // Set Turbopack root to frontend directory to avoid lockfile warning
  turbopack: {
    root: process.cwd(),
  },
  // Disable source maps to avoid source map warnings
  productionBrowserSourceMaps: false,
  images: {
    remotePatterns: [
      {
        protocol: 'https',
        hostname: '**',
      },
    ],
  },
  // Vercel optimizations
  compress: true,
  poweredByHeader: false,
  reactStrictMode: true,
  // Disable caching in development
  async headers() {
    return [
      {
        source: '/:path*',
        headers: [
          {
            key: 'Cache-Control',
            value: process.env.NODE_ENV === 'development' 
              ? 'no-store, no-cache, must-revalidate, proxy-revalidate, max-age=0'
              : 'public, s-maxage=60, stale-while-revalidate=300',
          },
        ],
      },
    ];
  },
};

export default withNextIntl(nextConfig);

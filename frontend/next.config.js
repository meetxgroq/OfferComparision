/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  experimental: {},
  env: {
    NEXT_PUBLIC_API_BASE: process.env.NEXT_PUBLIC_API_BASE || 'http://localhost:8001',
  },
  // Reduce EMFILE (too many open files) on macOS by using polling instead of native watchers
  webpack: (config, { dev }) => {
    if (dev) {
      config.watchOptions = {
        ...config.watchOptions,
        poll: 1000,
        ignored: ['**/node_modules', '**/.git'],
      };
    }
    return config;
  },
};

module.exports = nextConfig;



import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  /* config options here */
  outputFileTracingRoot: __dirname,
  images: {
    domains: ["books.google.com"],
  },
};

export default nextConfig;

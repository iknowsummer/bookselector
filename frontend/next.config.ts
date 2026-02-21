import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  output: "standalone",
  outputFileTracingRoot: __dirname,
  images: {
    domains: ["books.google.com"],
  },
};

export default nextConfig;

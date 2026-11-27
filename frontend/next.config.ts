import type { NextConfig } from "next";

// 画面からの /api/* はサーバ側（FastAPI）へ中継する。ブラウザから見ると同じ場所なので CORS の設定がいらない
const backend = process.env.BACKEND_URL ?? "http://127.0.0.1:8000";

const nextConfig: NextConfig = {
  async rewrites() {
    return [{ source: "/api/:path*", destination: `${backend}/api/:path*` }];
  },
};

export default nextConfig;

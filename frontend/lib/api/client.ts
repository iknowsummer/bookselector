/**
 * API のベース URL を返す。
 *
 * - サーバ側（Route Handler / Server Component）: `BACKEND_API_URL` を返し、
 *   FastAPI を内部ネットワーク経由で直接叩く。
 * - ブラウザ側（Client Component）: 同一オリジンの `/api` を返し、
 *   Next.js の Route Handler 経由で FastAPI へプロキシされる。
 */
export const getApiBaseUrl = (): string => {
  if (typeof window === "undefined") {
    const url = process.env.BACKEND_API_URL;
    if (!url) {
      throw new Error("BACKEND_API_URL環境変数が設定されていません");
    }
    return url;
  }
  return "/api";
};

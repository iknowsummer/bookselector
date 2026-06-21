import { getServerAccessToken } from "@/lib/auth/token";

function isServer(): boolean {
  return typeof window === "undefined";
}

/**
 * fetch ラッパー。
 *
 * サーバ側（Server Component / Route Handler 内）では `getServerAccessToken()`
 * で Auth0 アクセストークンを取得し `Authorization: Bearer ...` を付与する。
 *
 * ブラウザ側（Client Component）からは同一オリジンの `/api/*` を叩く構成のため、
 * トークン付与は Next.js の Route Handler 側に集約されている。ここではトークンを
 * 付けずに同一オリジン fetch をそのまま実行する（Cookie ベースのセッションで
 * Route Handler 側がユーザーを特定する）。
 *
 * 使用例（Server Component）:
 *   const data = await authenticatedFetch(`${apiBaseUrl}/books`);
 *
 * 使用例（Client Component）:
 *   const data = await authenticatedFetch("/api/books", { method: "POST", ... });
 */
export async function authenticatedFetch(
  url: string,
  options?: RequestInit,
): Promise<Response> {
  const headers = new Headers(options?.headers);

  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  if (isServer()) {
    const accessToken = await getServerAccessToken();
    if (accessToken) {
      headers.set("Authorization", `Bearer ${accessToken}`);
    }
  }

  return fetch(url, {
    ...options,
    headers,
  });
}

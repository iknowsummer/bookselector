import { getServerAccessToken, getClientAccessToken } from "@/lib/auth/token";

/**
 * サーバーまたはクライアントで実行中かを判定
 */
function isServer(): boolean {
  return typeof window === "undefined";
}

/**
 * 認証付きfetchラッパー - Authorizationヘッダーを自動追加
 *
 * Server Componentでの使用例:
 *   const data = await authenticatedFetch("/books");
 *
 * Client Componentでの使用例:
 *   const data = await authenticatedFetch("/books", { method: "POST", ... });
 */
export async function authenticatedFetch(
  url: string,
  options?: RequestInit,
): Promise<Response> {
  // コンテキストに基づいてトークンを取得
  const accessToken = isServer()
    ? await getServerAccessToken()
    : await getClientAccessToken();

  // 認証付きヘッダーを構築
  const headers = new Headers(options?.headers);

  // JSON API用にContent-Typeを常に設定
  if (!headers.has("Content-Type")) {
    headers.set("Content-Type", "application/json");
  }

  // トークンがあればAuthorizationヘッダーを追加
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  // 拡張ヘッダーでリクエストを実行
  return fetch(url, {
    ...options,
    headers,
  });
}

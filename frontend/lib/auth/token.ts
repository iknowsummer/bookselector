import { auth0, hasAuth0Error } from "@/lib/auth0";

/**
 * Server ComponentまたはServer Actionでアクセストークンを取得
 * これが推奨方法 - トークンはサーバー側に留まる
 */
export async function getServerAccessToken(): Promise<string | null> {
  // Auth0が初期化されていない場合はnullを返す
  if (hasAuth0Error) {
    return null;
  }

  try {
    const session = await auth0.getSession();
    if (!session) {
      return null;
    }

    const { token } = await auth0.getAccessToken();
    return token ?? null;
  } catch (error) {
    console.error("Failed to get server access token:", error);
    return null;
  }
}

/**
 * Client Componentでアクセストークンを取得
 * 組み込みの/auth/access-tokenエンドポイントを使用
 * 注意: トークンがブラウザに露出される
 */
export async function getClientAccessToken(): Promise<string | null> {
  try {
    const response = await fetch("/auth/access-token");
    if (!response.ok) {
      return null;
    }

    const data = await response.json();
    // Auth0 SDK v4では { token } 形式
    return data.token ?? null;
  } catch (error) {
    console.error("Failed to get client access token:", error);
    return null;
  }
}

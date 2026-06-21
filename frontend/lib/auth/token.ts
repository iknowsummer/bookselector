import { auth0, hasAuth0Error } from "@/lib/auth0";

/**
 * Server Component / Server Action / Route Handler 内で Auth0 アクセストークンを取得する。
 * トークンはサーバ側に留まる。
 */
export async function getServerAccessToken(): Promise<string | null> {
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

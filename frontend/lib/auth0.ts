import { Auth0Client } from "@auth0/nextjs-auth0/server";

let auth0Instance: Auth0Client | null = null;
let initializationError: Error | null = null;

try {
  auth0Instance = new Auth0Client({
    authorizationParameters: {
      audience: process.env.AUTH0_AUDIENCE,
      scope: "openid profile email offline_access",
    },
  });
} catch (error) {
  // 環境変数がない場合、エラーを記録するが、インスタンス化は進める
  initializationError =
    error instanceof Error ? error : new Error(String(error));
  console.warn("Auth0 initialization warning:", initializationError.message);
}

export const auth0 = auth0Instance as Auth0Client;
export const hasAuth0Error = !!initializationError;

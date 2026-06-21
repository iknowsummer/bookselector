import { NextRequest, NextResponse } from "next/server";
import { getServerAccessToken } from "@/lib/auth/token";

/**
 * FastAPI への汎用プロキシ Route Handler。
 *
 * ブラウザは同一オリジン `/api/<path>` を叩き、ここでサーバ側で Auth0 アクセストークンを
 * 付与した上で `BACKEND_API_URL/<path>` へ転送する。これによりブラウザにはアクセス
 * トークンが露出せず、CORS も不要になる。
 *
 * クエリ文字列・リクエストボディ・Content-Type はそのまま素通しする。
 * lookup のような認証不要エンドポイントにもトークンを付けて送るが、FastAPI 側で
 * 単に無視されるため動作上の問題はない（パスベースの分岐を避けてシンプルに保つ）。
 */
async function proxy(
  request: NextRequest,
  { params }: { params: Promise<{ path: string[] }> },
): Promise<NextResponse> {
  const backendBase = process.env.BACKEND_API_URL;
  if (!backendBase) {
    return NextResponse.json(
      { error: "BACKEND_API_URL is not configured" },
      { status: 500 },
    );
  }

  const { path } = await params;
  const url = new URL(request.url);
  const target = `${backendBase}/${path.join("/")}${url.search}`;

  const headers = new Headers();
  const contentType = request.headers.get("content-type");
  if (contentType) {
    headers.set("content-type", contentType);
  }
  const accept = request.headers.get("accept");
  if (accept) {
    headers.set("accept", accept);
  }

  const accessToken = await getServerAccessToken();
  if (accessToken) {
    headers.set("Authorization", `Bearer ${accessToken}`);
  }

  const init: RequestInit = {
    method: request.method,
    headers,
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = await request.text();
  }

  const upstream = await fetch(target, init);

  const responseHeaders = new Headers();
  const upstreamContentType = upstream.headers.get("content-type");
  if (upstreamContentType) {
    responseHeaders.set("content-type", upstreamContentType);
  }

  return new NextResponse(upstream.body, {
    status: upstream.status,
    headers: responseHeaders,
  });
}

export const GET = proxy;
export const POST = proxy;
export const PUT = proxy;
export const PATCH = proxy;
export const DELETE = proxy;

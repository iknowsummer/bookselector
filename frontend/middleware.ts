import type { NextRequest } from "next/server";
import { NextResponse } from "next/server";
import { auth0 } from "./lib/auth0";

// 認証必須のパスパターン
const protectedPaths = ["/books/new", "/dashboard", "/shelves/new"];

// 動的パス（編集ページ）のパターン
const protectedPatterns = [/^\/books\/\d+\/edit$/, /^\/shelves\/\d+\/edit$/];

function isProtectedPath(pathname: string): boolean {
  if (protectedPaths.some((path) => pathname.startsWith(path))) {
    return true;
  }
  return protectedPatterns.some((pattern) => pattern.test(pathname));
}

export async function middleware(request: NextRequest) {
  const authRes = await auth0.middleware(request);

  // 保護対象パスの場合、セッションをチェック
  if (isProtectedPath(request.nextUrl.pathname)) {
    const session = await auth0.getSession();
    if (!session) {
      const loginUrl = new URL("/auth/login", request.url);
      loginUrl.searchParams.set("returnTo", request.nextUrl.pathname);
      return NextResponse.redirect(loginUrl);
    }
  }

  return authRes;
}

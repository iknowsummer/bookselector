import { auth0 } from "@/lib/auth0";

export default async function LoginStatus() {
  const session = await auth0.getSession();

  if (!session) {
    return <a href="/auth/login">ログイン</a>;
  }

  return (
    <>
      <a href="/auth/logout">ログアウト</a>
    </>
  );
}

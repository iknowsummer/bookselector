import { redirect } from "next/navigation";
import { auth0 } from "@/lib/auth0";

export default async function Dashboard() {
  const session = await auth0.getSession();
  if (!session) {
    // 未ログインならリダイレクト
    redirect("/auth/login");
  }

  return (
    <div>
      ようこそ {session.user.name} / {session.user.email}
    </div>
  );
}

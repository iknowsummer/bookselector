import Link from "next/link";
import { ShelfList } from "@/app/shelves/_components/ShelfList";
import LoginPrompt from "@/app/components/LoginPrompt";
import { auth0 } from "@/lib/auth0";

export default async function ShelfListPage() {
  const session = await auth0.getSession();

  if (!session) {
    return <LoginPrompt title="棚一覧を見るにはログインが必要です" />;
  }

  return (
    <div className="container">
      <div className="page-header">
        <h2>棚一覧</h2>
        <Link href="/shelves/new">
          <button type="button" className="button">棚を追加</button>
        </Link>
      </div>
      <ShelfList />
    </div>
  );
}

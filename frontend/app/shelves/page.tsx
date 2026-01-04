import Link from "next/link";
import { ShelfList } from "@/app/shelves/_components/ShelfList";

export default async function ShelfListPage() {
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

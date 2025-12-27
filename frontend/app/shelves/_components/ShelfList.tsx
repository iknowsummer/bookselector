import Link from "next/link";
import { fetchShelves } from "@/lib/api/shelves";

export async function ShelfList() {
  const shelves = await fetchShelves();

  if (shelves.length === 0) {
    return <div>登録済みの棚はありません</div>;
  }

  return (
    <div className="shelf-list">
      {shelves.map((shelf) => (
        <Link key={shelf.id} href={`/shelves/${shelf.id}/edit`} className="shelf-list-item">
          <span className="shelf-name">{shelf.name}</span>
          <span className="shelf-memo">{shelf.memo ?? "-"}</span>
        </Link>
      ))}
    </div>
  );
}

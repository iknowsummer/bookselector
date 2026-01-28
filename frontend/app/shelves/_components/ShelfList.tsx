import Link from "next/link";
import type { Shelf } from "@/types/shelf";
import { fetchShelves } from "@/lib/api/shelves";

export async function ShelfList() {
  let shelves: Shelf[] = [];
  let fetchError: string | null = null;

  try {
    shelves = await fetchShelves();
  } catch (error) {
    console.error("Failed to fetch shelves:", error);
    fetchError =
      error instanceof Error ? error.message : "棚情報の取得に失敗しました";
  }

  if (fetchError) {
    return <div style={{ color: "#d32f2f" }}>⚠️ {fetchError}</div>;
  }

  if (shelves.length === 0) {
    return <div>登録済みの棚はありません</div>;
  }

  return (
    <div className="shelf-list">
      {shelves.map((shelf) => (
        <Link
          key={shelf.id}
          href={`/shelves/${shelf.id}/edit`}
          className="shelf-list-item"
        >
          <span className="shelf-name">{shelf.name}</span>
          <span className="shelf-memo">{shelf.memo ?? "-"}</span>
        </Link>
      ))}
    </div>
  );
}

import Link from "next/link";
import type { Shelf } from "@/types/shelf";

type Props = {
  shelves: Shelf[];
  error?: string;
  isLoading?: boolean;
};

export function ShelfList({ shelves, error, isLoading }: Props) {
  if (isLoading) {
    return <div>棚情報を取得中です...</div>;
  }

  if (error) {
    return <div className="error">エラー: {error}</div>;
  }

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

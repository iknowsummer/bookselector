import Link from "next/link";
import type { Shelf } from "@/types/shelf";

type Props = {
  shelf: Shelf;
};

export function ShelfDetail({ shelf }: Props) {
  return (
    <div className="shelf-detail">
      <h2>棚詳細</h2>
      <dl>
        <dt>名称</dt>
        <dd>{shelf.name}</dd>
        <dt>メモ</dt>
        <dd>{shelf.memo ?? "-"}</dd>
      </dl>
      <div className="form-actions">
        <Link href={`/shelves/${shelf.id}/edit`}>
          <button type="button">編集</button>
        </Link>
        <Link href="/shelves">
          <button type="button">一覧に戻る</button>
        </Link>
      </div>
    </div>
  );
}

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
    <table className="shelf-table">
      <thead>
        <tr>
          <th>名称</th>
          <th>メモ</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        {shelves.map((shelf) => (
          <tr key={shelf.id}>
            <td>{shelf.name}</td>
            <td>{shelf.memo ?? "-"}</td>
            <td>
              <div className="table-actions">
                <Link href={`/shelves/${shelf.id}`}>詳細</Link>
                <Link href={`/shelves/${shelf.id}/edit`}>編集</Link>
              </div>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

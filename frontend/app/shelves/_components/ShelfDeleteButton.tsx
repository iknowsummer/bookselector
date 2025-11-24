"use client";

import { useState } from "react";

type Props = {
  onDelete: () => Promise<void>;
};

export function ShelfDeleteButton({ onDelete }: Props) {
  const [error, setError] = useState<string>("");
  const [isDeleting, setIsDeleting] = useState<boolean>(false);

  const handleClick = async () => {
    if (!confirm("本当に削除しますか？")) {
      return;
    }
    setIsDeleting(true);
    setError("");
    try {
      await onDelete();
    } catch (err) {
      setError(`${err}`);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="shelf-delete">
      <button type="button" onClick={handleClick} disabled={isDeleting}>
        {isDeleting ? "削除中..." : "棚を削除"}
      </button>
      {error && <div className="error">エラー: {error}</div>}
    </div>
  );
}

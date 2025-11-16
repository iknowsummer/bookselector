"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { deleteBook } from "@/lib/api/books";

type DeleteButtonProps = {
  bookId: number;
  bookTitle: string;
  onSuccess?: () => void;
};

export default function DeleteButton({
  bookId,
  bookTitle,
  onSuccess,
}: DeleteButtonProps) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    const confirmed = window.confirm(
      `「${bookTitle}」を削除してもよろしいですか？`
    );
    if (!confirmed) return;

    setIsDeleting(true);
    try {
      await deleteBook(bookId);
      if (onSuccess) {
        onSuccess();
      } else {
        // デフォルトの挙動: 一覧ページへ遷移
        router.push("/books");
      }
    } catch (err) {
      alert(`削除に失敗しました: ${err}`);
      setIsDeleting(false);
    }
  };

  return (
    <button
      onClick={handleDelete}
      disabled={isDeleting}
      className="delete-button"
    >
      {isDeleting ? "削除中..." : "削除"}
    </button>
  );
}

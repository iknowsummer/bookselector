"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Image from "next/image";
import Link from "next/link";
import { fetchBook, deleteBook } from "@/lib/api/books";
import type { Book } from "@/types/book";

export default function BookDetailPage() {
  const router = useRouter();
  const params = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [error, setError] = useState<string>("");
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const getData = async () => {
      try {
        const id = Number(params.id);
        const data = await fetchBook(id);
        setBook(data);
      } catch (err) {
        setError(`書籍の取得に失敗しました: ${err}`);
      }
    };
    getData();
  }, [params.id]);

  const handleDelete = async () => {
    if (!book) return;

    const confirmed = window.confirm(
      `「${book.title}」を削除してもよろしいですか？`
    );
    if (!confirmed) return;

    setIsDeleting(true);
    try {
      await deleteBook(book.id);
      router.push("/books");
    } catch (err) {
      setError(`削除に失敗しました: ${err}`);
      setIsDeleting(false);
    }
  };

  if (error) {
    return (
      <div className="container">
        <div className="error">エラー: {error}</div>
        <Link href="/books">
          <button>書籍一覧に戻る</button>
        </Link>
      </div>
    );
  }

  if (!book) {
    return <div className="container">読み込み中...</div>;
  }

  return (
    <div className="container">
      <div className="book-detail">
        <h2>{book.title}</h2>

        <div className="book-detail-content">
          {book.image_url && (
            <div className="book-detail-image">
              <Image
                src={book.image_url}
                alt={book.title}
                width={200}
                height={300}
              />
            </div>
          )}

          <div className="book-detail-info">
            <div className="info-row">
              <span className="info-label">著者:</span>
              <span>{book.author}</span>
            </div>

            {book.description && (
              <div className="info-row">
                <span className="info-label">説明:</span>
                <p>{book.description}</p>
              </div>
            )}

            {book.note && (
              <div className="info-row">
                <span className="info-label">メモ:</span>
                <p>{book.note}</p>
              </div>
            )}
          </div>
        </div>

        <div className="book-detail-actions">
          <Link href="/books">
            <button>一覧に戻る</button>
          </Link>
          <button
            onClick={handleDelete}
            disabled={isDeleting}
            className="delete-button"
          >
            {isDeleting ? "削除中..." : "削除"}
          </button>
        </div>
      </div>
    </div>
  );
}

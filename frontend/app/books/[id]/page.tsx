"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import Link from "next/link";
import { fetchBook } from "@/lib/api/books";
import type { Book } from "@/types/book";
import BookDetail from "@/components/BookDetail";
import DeleteButton from "@/components/DeleteButton";

export default function BookDetailPage() {
  const router = useRouter();
  const params = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [error, setError] = useState<string>("");

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
      <BookDetail
        book={book}
        deleteButton={
          <DeleteButton
            bookId={book.id}
            bookTitle={book.title}
            onSuccess={() => router.push("/books")}
          />
        }
      />
    </div>
  );
}

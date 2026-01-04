"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import Link from "next/link";
import { fetchBook } from "@/lib/api/books";
import { fetchShelf } from "@/lib/api/shelves";
import type { Book } from "@/types/book";
import type { Shelf } from "@/types/shelf";
import BookDetail from "@/app/books/_components/BookDetail";

export default function BookDetailPage() {
  const params = useParams();
  const [book, setBook] = useState<Book | null>(null);
  const [shelf, setShelf] = useState<Shelf | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const getData = async () => {
      try {
        const id = Number(params.id);
        const data = await fetchBook(id);
        setBook(data);

        // 棚IDが存在する場合は棚情報も取得
        if (data.shelf_id) {
          try {
            const shelfData = await fetchShelf(data.shelf_id);
            setShelf(shelfData);
          } catch (err) {
            console.error("棚情報の取得に失敗しました:", err);
            // 棚の取得に失敗しても書籍表示は続行
          }
        }
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
          <button className="button">書籍一覧に戻る</button>
        </Link>
      </div>
    );
  }

  if (!book) {
    return <div className="container">読み込み中...</div>;
  }

  return (
    <div className="container">
      <BookDetail book={book} shelf={shelf} />
    </div>
  );
}

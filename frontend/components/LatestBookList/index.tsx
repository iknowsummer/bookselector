"use client";
import { useState, useEffect } from "react";
import type { Book } from "@/types/book";
import { fetchLatestBooks } from "@/lib/api/books";
import { BookList } from "@/components/BookList";

type LatestBookListProps = {
  limit?: number;
};

export default function LatestBookList({ limit = 12 }: LatestBookListProps) {
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const loadLatestBooks = async () => {
      setIsLoading(true);
      setError("");
      try {
        const data = await fetchLatestBooks(limit);
        setBooks(data);
        if (data.length === 0) {
          setError("取得できる書籍情報がありませんでした");
        }
      } catch (err) {
        setBooks([]);
        setError(`書籍情報の取得に失敗しました: ${err}`);
      } finally {
        setIsLoading(false);
      }
    };

    loadLatestBooks();
  }, [limit]);

  return (
    <section>
      {isLoading ? (
        <div>書籍情報を取得中です...</div>
      ) : error ? (
        <div>{error}</div>
      ) : (
        <BookList books={books} />
      )}
    </section>
  );
}

"use client";
import { useState, useEffect } from "react";
import type { Book } from "@/types/book";
import { fetchRandomBooks } from "@/lib/api/books";
import { BookList } from "@/components/BookList";

type RandomBookListProps = {
  showButton?: boolean;
};

export default function RandomBookList({
  showButton = true,
}: RandomBookListProps) {
  const [books, setBooks] = useState<Book[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>("");

  const handleFetchRandomBooks = async () => {
    setIsLoading(true);
    setError("");
    try {
      const data = await fetchRandomBooks();
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

  useEffect(() => {
    handleFetchRandomBooks();
  }, []);

  return (
    <section>
      {isLoading ? (
        <div>書籍情報を取得中です...</div>
      ) : error ? (
        <div>{error}</div>
      ) : (
        <BookList books={books} />
      )}
      {showButton && (
        <button type="button" onClick={handleFetchRandomBooks}>
          ランダム再読込
        </button>
      )}
    </section>
  );
}

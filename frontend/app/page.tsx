"use client";
import { useState, useEffect } from "react";
import type { Book } from "@/types/book";
import { fetchRandomBooks } from "@/lib/api/books";
import { BookList } from "@/components/BookList";

export default function Home() {
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
        setError("書籍情報が見つかりませんでした");
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
    <main>
      <section>
        <h1>ランダム取得</h1>
      </section>
      <section>
        <button type="button" onClick={handleFetchRandomBooks}>
          ランダム再読込
        </button>
        {isLoading ? (
          <div>書籍情報を取得中です...</div>
        ) : error ? (
          <div>{error}</div>
        ) : (
          <BookList books={books} />
        )}
      </section>
    </main>
  );
}

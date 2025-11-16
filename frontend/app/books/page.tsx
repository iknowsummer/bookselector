"use client";

import { useEffect, useState } from "react";
import type { Book } from "@/types/book";
import { fetchBooks } from "@/lib/api/books";
import { BookList } from "@/app/books/_components/BookList";

export default function Home() {
  const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const getData = async () => {
      setIsLoading(true);
      setError("");
      try {
        const data = await fetchBooks();
        setBooks(data);
      } catch (err) {
        setError(`API取得エラー: ${err}`);
      } finally {
        setIsLoading(false);
      }
    };
    getData();
  }, []);

  return (
    <div>
      <h2>書籍一覧</h2>
      <BookList books={books} error={error} isLoading={isLoading} />
    </div>
  );
}

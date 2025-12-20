"use client";
import { useState, useEffect } from "react";
import type { Book } from "@/types/book";
import { fetchRandomBooks } from "@/lib/api/books";
import { BookList } from "@/app/books/_components/BookList";

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
      <BookList books={books} error={error} isLoading={isLoading} />
      {showButton && (
        <button type="button" onClick={handleFetchRandomBooks} className="button">
          ランダム再読込
        </button>
      )}
    </section>
  );
}

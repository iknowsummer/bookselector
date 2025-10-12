"use client";
import { useState } from "react";
import type { Book } from "@/types/book";
import { fetchRandomBooks } from "@/lib/api/books";
import { BookList } from "@/components/BookList";

export default function Home() {
  const [books, setBooks] = useState<Book[]>([]);
  const [message, setMessage] = useState<string>("");

  const handleFetchRandomBooks = async () => {
    setMessage("書籍情報を取得中です...");
    try {
      const data = await fetchRandomBooks();
      setBooks(data);
      if (data.length === 0) {
        setMessage("取得できる書籍情報がありませんでした");
      } else {
        setMessage("書籍情報を取得しました");
      }
    } catch (error) {
      setBooks([]);
      setMessage(`書籍情報の取得に失敗しました: ${error}`);
    }
  };

  return (
    <main>
      <section>
        <h1>ランダム取得</h1>
      </section>
      <section>
        <button type="button" onClick={handleFetchRandomBooks}>
          ランダム再読込
        </button>
        <div>{message}</div>
        <BookList books={books} />
      </section>
    </main>
  );
}

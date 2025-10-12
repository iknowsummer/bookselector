"use client";
import { useState } from "react";

type Book = {
  id: number;
  title: string;
  author: string;
  description?: string | null;
  note?: string | null;
};

export default function Home() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const [books, setBooks] = useState<Book[]>([]);
  const [message, setMessage] = useState<string>("");

  const fetchRandomBooks = async () => {
    setMessage("書籍情報を取得中です...");
    try {
      const res = await fetch(`${apiBaseUrl}/books/random/`);
      if (!res.ok) {
        throw new Error("書籍情報の取得に失敗しました");
      }
      const data: Book[] = await res.json();
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
        <h1>Book Selector</h1>
      </section>
      <section>
        <button type="button" onClick={fetchRandomBooks}>
          ランダムに書籍情報を取得
        </button>
        <div>{message}</div>
        <ul>
          {books.map((book) => (
            <li key={book.id}>
              <div>タイトル: {book.title}</div>
              <div>著者: {book.author}</div>
              {book.description ? <div>説明: {book.description}</div> : null}
              {book.note ? <div>メモ: {book.note}</div> : null}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

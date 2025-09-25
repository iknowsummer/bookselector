"use client";
import { useEffect, useState } from "react";

type Book = {
  id: number;
  title: string;
  author: string;
  description?: string | null;
  note?: string | null;
};

export default function Home() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const [apiStatus, setApiStatus] = useState<string>("");
  const [books, setBooks] = useState<Book[]>([]);
  const [message, setMessage] = useState<string>("");

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch(apiBaseUrl);
        if (!res.ok) {
          throw new Error("APIの取得に失敗しました");
        }
        const text = await res.text();
        setApiStatus(text);
      } catch (error) {
        setApiStatus("APIステータスの取得に失敗しました");
      }
    };
    fetchStatus();
  }, [apiBaseUrl]);

  const fetchRandomBooks = async () => {
    setMessage("書籍情報を取得中です...");
    try {
      const res = await fetch(`${apiBaseUrl}/books/pick/`);
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
      setMessage("書籍情報の取得に失敗しました");
    }
  };

  return (
    <main>
      <section>
        <h1>Book Selector</h1>
        <div>APIレスポンス: {apiStatus}</div>
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

"use client";

import Image from "next/image";
import { useEffect, useState } from "react";

interface Book {
  id: number;
  title: string;
  author: string;
  image_url: string;
}

export default function Home() {
  const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(
          `${process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"}/books`
        );
        const data = await res.json();
        setBooks(data);
      } catch (err) {
        setError(`API取得エラー: ${err}`);
      }
    };
    fetchData();
  }, []);

  return (
    <>
      {error ? (
        <div>エラー: {error}</div>
      ) : (
        <div>
          <h2>書籍一覧</h2>
          <ul className="book-list">
            {books.map((book) => (
              <li key={book.id}>
                <div className="book-image">
                  {book.image_url ? (
                    <Image
                      src={book.image_url}
                      alt={book.title}
                      width={128}
                      height={200}
                    />
                  ) : (
                    <span className="noimage">No Image</span>
                  )}
                </div>
                <div className="book-title">{book.title ?? ""}</div>
                <div className="book-author">{book.author ?? ""}</div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}

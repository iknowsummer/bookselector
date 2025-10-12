"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import type { Book } from "@/types/book";
import { fetchBooks } from "@/lib/api/books";

export default function Home() {
  const [books, setBooks] = useState<Book[]>([]);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const getData = async () => {
      try {
        const data = await fetchBooks();
        setBooks(data);
      } catch (err) {
        setError(`API取得エラー: ${err}`);
      }
    };
    getData();
  }, []);

  return (
    <>
      {error ? (
        <div>エラー: {error}</div>
      ) : (
        <div>
          <div className="header-with-button">
            <h2>書籍一覧</h2>
            <Link href="/books/new">
              <button>新規登録</button>
            </Link>
          </div>
          <ul className="book-list">
            {books.map((book) => (
              <li key={book.id}>
                <Link href={`/books/${book.id}`}>
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
                </Link>
              </li>
            ))}
          </ul>
        </div>
      )}
    </>
  );
}

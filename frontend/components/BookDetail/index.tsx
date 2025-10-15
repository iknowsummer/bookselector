"use client";

import Image from "next/image";
import Link from "next/link";
import type { Book } from "@/types/book";

type BookDetailProps = {
  book: Book;
};

export default function BookDetail({ book }: BookDetailProps) {
  return (
    <div className="book-detail">
      <div className="book-detail-content">
        <div className="book-detail-image">
          {book.image_url ? (
            <Image
              src={book.image_url}
              alt={book.title}
              width={200}
              height={300}
            />
          ) : (
            <div className="noimage">NO IMAGE</div>
          )}
        </div>

        <h2>{book.title}</h2>

        <div className="book-detail-info">
          <div className="info-row">
            <span className="info-label">著者:</span>
            <span>{book.author}</span>
          </div>

          {book.isbn && (
            <div className="info-row">
              <span className="info-label">ISBN:</span>
              <span>{book.isbn}</span>
            </div>
          )}

          {book.description && (
            <div className="info-row">
              <span className="info-label">説明:</span>
              <p>{book.description}</p>
            </div>
          )}

          {book.note && (
            <div className="info-row">
              <span className="info-label">メモ:</span>
              <p>{book.note}</p>
            </div>
          )}
        </div>
      </div>

      <div className="book-detail-actions">
        <Link href={`/books/${book.id}/edit`}>
          <button>編集</button>
        </Link>
      </div>
    </div>
  );
}

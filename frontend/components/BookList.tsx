import Link from "next/link";
import Image from "next/image";
import type { Book } from "@/types/book";

type BookListProps = {
  books: Book[];
};

export function BookList({ books }: BookListProps) {
  return (
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
  );
}

import Link from "next/link";
import Image from "next/image";
import type { Book } from "@/types/book";

type BookListProps = {
  books: Book[];
  error?: string;
  isLoading?: boolean;
};

export function BookList({ books, error, isLoading }: BookListProps) {
  if (isLoading) {
    return <div>書籍情報を取得中です...</div>;
  }

  if (error) {
    return <div>エラー: {error}</div>;
  }

  if (books.length === 0) {
    return <div>書籍情報がありません</div>;
  }

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

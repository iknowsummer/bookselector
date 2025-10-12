import type { Book } from "@/types/book";

type BookListProps = {
  books: Book[];
};

export function BookList({ books }: BookListProps) {
  return (
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
  );
}

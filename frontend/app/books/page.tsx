import type { Book } from "@/types/book";
import { fetchBooks } from "@/lib/api/books";
import { fetchShelves } from "@/lib/api/shelves";
import { BookList } from "@/app/books/_components/BookList";
import ShelfFilter from "@/app/books/_components/ShelfFilter";

interface PageProps {
  searchParams: Promise<{
    [key: string]: string | string[] | undefined;
  }>;
}

export default async function BooksPage({ searchParams }: PageProps) {
  const params = await searchParams;

  // searchParamsからshelfパラメータを抽出
  const shelfParam = params.shelf;
  let selectedShelfId: number | null | "unassigned" = null;

  if (shelfParam === "unassigned") {
    selectedShelfId = "unassigned";
  } else if (shelfParam && typeof shelfParam === "string") {
    const parsed = parseInt(shelfParam, 10);
    if (!isNaN(parsed)) {
      selectedShelfId = parsed;
    }
  }

  // サーバーサイドでデータフェッチ
  const books = await fetchBooks(selectedShelfId);
  const shelves = await fetchShelves();

  return (
    <div>
      <h2>書籍一覧</h2>
      <ShelfFilter shelves={shelves} selectedShelfId={selectedShelfId} />
      <BookList books={books} />
    </div>
  );
}

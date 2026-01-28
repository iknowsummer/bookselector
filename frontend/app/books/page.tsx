import type { Book } from "@/types/book";
import type { Shelf } from "@/types/shelf";
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

  // サーバーサイドでデータフェッチ（エラーハンドリング付き）
  let books: Book[] = [];
  let shelves: Shelf[] = [];
  let fetchError: string | null = null;

  try {
    books = await fetchBooks(selectedShelfId);
  } catch (error) {
    console.error("Failed to fetch books:", error);
    fetchError =
      error instanceof Error ? error.message : "書籍情報の取得に失敗しました";
  }

  try {
    shelves = await fetchShelves();
  } catch (error) {
    console.error("Failed to fetch shelves:", error);
    // shelvesはフィルターに必要なので、エラーメッセージのみ記録
  }

  return (
    <div>
      <h2>書籍一覧</h2>
      <ShelfFilter shelves={shelves} selectedShelfId={selectedShelfId} />
      {fetchError && (
        <div style={{ color: "#d32f2f", marginBottom: "16px" }}>
          ⚠️ {fetchError}
        </div>
      )}
      <BookList books={books} />
    </div>
  );
}

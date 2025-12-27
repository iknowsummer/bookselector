"use client";

import { useEffect, useState, Suspense } from "react";
import { useRouter } from "next/navigation";
import type { Book } from "@/types/book";
import { fetchBooks } from "@/lib/api/books";
import { BookList } from "@/app/books/_components/BookList";
import ShelfFilter from "@/app/books/_components/ShelfFilter";
import { ShelfParamReader } from "@/app/books/_components/ShelfParamReader";

export default function Home() {
  const router = useRouter();

  const [books, setBooks] = useState<Book[]>([]);
  const [selectedShelfId, setSelectedShelfId] = useState<
    number | null | "unassigned"
  >(null);
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  // ShelfParamReaderからのコールバック
  const handleShelfRead = (shelfId: number | null | "unassigned") => {
    setSelectedShelfId(shelfId);
  };

  // 書籍一覧を取得（フィルター変更時に再実行）
  useEffect(() => {
    const getData = async () => {
      setIsLoading(true);
      setError("");
      try {
        const data = await fetchBooks(selectedShelfId);
        setBooks(data);
      } catch (err) {
        setError(`API取得エラー: ${err}`);
      } finally {
        setIsLoading(false);
      }
    };
    getData();
  }, [selectedShelfId]);

  // フィルター変更時にURLを更新
  const handleShelfChange = (shelfId: number | null | "unassigned") => {
    setSelectedShelfId(shelfId);

    // URLパラメータを更新
    const params = new URLSearchParams();
    if (shelfId === "unassigned") {
      params.set("shelf", "unassigned");
    } else if (shelfId !== null) {
      params.set("shelf", shelfId.toString());
    }

    const queryString = params.toString();
    const newUrl = queryString ? `/books?${queryString}` : "/books";
    router.push(newUrl, { scroll: false });
  };

  return (
    <div>
      <Suspense fallback={null}>
        <ShelfParamReader onShelfIdRead={handleShelfRead} />
      </Suspense>
      <h2>書籍一覧</h2>
      <ShelfFilter
        selectedShelfId={selectedShelfId}
        onShelfChange={handleShelfChange}
      />
      <BookList books={books} error={error} isLoading={isLoading} />
    </div>
  );
}

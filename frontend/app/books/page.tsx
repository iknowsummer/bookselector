"use client";

import { useEffect, useState } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import type { Book } from "@/types/book";
import type { Shelf } from "@/types/shelf";
import { fetchBooks } from "@/lib/api/books";
import { fetchShelves } from "@/lib/api/shelves";
import { BookList } from "@/app/books/_components/BookList";
import ShelfFilter from "@/app/books/_components/ShelfFilter";

export default function Home() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [books, setBooks] = useState<Book[]>([]);
  const [shelves, setShelves] = useState<Shelf[]>([]);
  const [selectedShelfId, setSelectedShelfId] = useState<
    number | null | "unassigned"
  >(null);
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isLoadingShelves, setIsLoadingShelves] = useState<boolean>(true);

  // URLパラメータから初期値を読み込む
  useEffect(() => {
    const shelfParam = searchParams.get("shelf");
    if (shelfParam === "unassigned") {
      setSelectedShelfId("unassigned");
    } else if (shelfParam) {
      const shelfId = parseInt(shelfParam, 10);
      if (!isNaN(shelfId)) {
        setSelectedShelfId(shelfId);
      }
    }
  }, [searchParams]);

  // 棚一覧を取得
  useEffect(() => {
    const getShelves = async () => {
      setIsLoadingShelves(true);
      try {
        const data = await fetchShelves();
        setShelves(data);
      } catch (err) {
        console.error("棚一覧の取得に失敗しました:", err);
      } finally {
        setIsLoadingShelves(false);
      }
    };
    getShelves();
  }, []);

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
      <h2>書籍一覧</h2>
      <ShelfFilter
        selectedShelfId={selectedShelfId}
        onShelfChange={handleShelfChange}
        shelves={shelves}
        isLoading={isLoadingShelves}
      />
      <BookList books={books} error={error} isLoading={isLoading} />
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { ShelfDetail } from "@/app/shelves/_components/ShelfDetail";
import { fetchShelf } from "@/lib/api/shelves";
import type { Shelf } from "@/types/shelf";

export default function ShelfDetailPage() {
  const params = useParams();
  const [shelf, setShelf] = useState<Shelf | null>(null);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    const load = async () => {
      setError("");
      try {
        const id = Number(params.id);
        const data = await fetchShelf(id);
        setShelf(data);
      } catch (err) {
        setError(`${err}`);
      }
    };
    load();
  }, [params.id]);

  if (error) {
    return <div className="container">エラー: {error}</div>;
  }

  if (!shelf) {
    return <div className="container">読み込み中...</div>;
  }

  return (
    <div className="container">
      <ShelfDetail shelf={shelf} />
    </div>
  );
}

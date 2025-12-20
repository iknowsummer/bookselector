"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import type { Shelf } from "@/types/shelf";
import { fetchShelves } from "@/lib/api/shelves";
import { ShelfList } from "@/app/shelves/_components/ShelfList";

export default function ShelfListPage() {
  const [shelves, setShelves] = useState<Shelf[]>([]);
  const [error, setError] = useState<string>("");
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const load = async () => {
      setIsLoading(true);
      setError("");
      try {
        const data = await fetchShelves();
        setShelves(data);
      } catch (err) {
        setError(`${err}`);
      } finally {
        setIsLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="container">
      <div className="page-header">
        <h2>棚一覧</h2>
        <Link href="/shelves/new">
          <button type="button" className="button">棚を追加</button>
        </Link>
      </div>
      <ShelfList shelves={shelves} error={error} isLoading={isLoading} />
    </div>
  );
}

"use client";

import { useEffect, useState } from "react";
import { Shelf } from "@/types/shelf";
import { fetchShelves } from "@/lib/api/shelves";
import styles from "./ShelfFilter.module.css";

type ShelfFilterProps = {
  selectedShelfId: number | null | "unassigned";
  onShelfChange: (shelfId: number | null | "unassigned") => void;
};

export default function ShelfFilter({
  selectedShelfId,
  onShelfChange,
}: ShelfFilterProps) {
  const [shelves, setShelves] = useState<Shelf[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    const loadShelves = async () => {
      setIsLoading(true);
      try {
        const data = await fetchShelves();
        setShelves(data);
      } catch (err) {
        console.error("棚一覧の取得に失敗しました:", err);
      } finally {
        setIsLoading(false);
      }
    };
    loadShelves();
  }, []);

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;
    if (value === "") {
      onShelfChange(null);
    } else if (value === "unassigned") {
      onShelfChange("unassigned");
    } else {
      onShelfChange(parseInt(value, 10));
    }
  };

  return (
    <div className={styles.container}>
      <label htmlFor="shelf-filter" className={styles.label}>
        書棚でフィルタ
      </label>
      <select
        id="shelf-filter"
        value={selectedShelfId ?? ""}
        onChange={handleChange}
        disabled={isLoading}
        className={styles.select}
      >
        <option value="">すべての棚</option>
        <option value="unassigned">未登録</option>
        {shelves.map((shelf) => (
          <option key={shelf.id} value={shelf.id}>
            {shelf.name}
          </option>
        ))}
      </select>
    </div>
  );
}

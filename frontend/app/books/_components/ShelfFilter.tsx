"use client";

import { useRouter } from "next/navigation";
import { Shelf } from "@/types/shelf";
import styles from "./ShelfFilter.module.css";

type ShelfFilterProps = {
  shelves: Shelf[];
  selectedShelfId: number | null | "unassigned";
};

export default function ShelfFilter({
  shelves,
  selectedShelfId,
}: ShelfFilterProps) {
  const router = useRouter();

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const value = e.target.value;

    const params = new URLSearchParams();
    if (value === "unassigned") {
      params.set("shelf", "unassigned");
    } else if (value !== "") {
      params.set("shelf", value);
    }

    const queryString = params.toString();
    const newUrl = queryString ? `/books?${queryString}` : "/books";
    router.push(newUrl, { scroll: false });
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

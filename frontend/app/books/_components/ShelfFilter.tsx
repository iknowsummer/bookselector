"use client";

import { Shelf } from "@/types/shelf";

type ShelfFilterProps = {
  selectedShelfId: number | null | "unassigned";
  onShelfChange: (shelfId: number | null | "unassigned") => void;
  shelves: Shelf[];
  isLoading: boolean;
};

export default function ShelfFilter({
  selectedShelfId,
  onShelfChange,
  shelves,
  isLoading,
}: ShelfFilterProps) {
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
    <div className="mb-6">
      <label htmlFor="shelf-filter" className="block text-sm font-medium mb-2">
        書棚でフィルタ
      </label>
      <select
        id="shelf-filter"
        value={selectedShelfId ?? ""}
        onChange={handleChange}
        disabled={isLoading}
        className="block w-full md:w-64 px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:bg-gray-100 disabled:cursor-not-allowed"
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

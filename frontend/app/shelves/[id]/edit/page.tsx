"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import Link from "next/link";
import { ShelfForm } from "@/app/shelves/_components/ShelfForm";
import { ShelfDeleteButton } from "@/app/shelves/_components/ShelfDeleteButton";
import { deleteShelf, fetchShelf, updateShelf } from "@/lib/api/shelves";
import type { Shelf, ShelfFormData } from "@/types/shelf";

export default function EditShelfPage() {
  const params = useParams();
  const router = useRouter();
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

  const handleSubmit = async (data: ShelfFormData) => {
    if (!shelf) return;
    await updateShelf(shelf.id, data);
    router.push("/shelves");
  };

  const handleDelete = async () => {
    if (!shelf) return;
    await deleteShelf(shelf.id);
    router.push("/shelves");
  };

  if (error) {
    return <div className="container">エラー: {error}</div>;
  }

  if (!shelf) {
    return <div className="container">読み込み中...</div>;
  }

  return (
    <div className="container">
      <h2>棚の編集</h2>
      <ShelfForm
        initialData={{ name: shelf.name, memo: shelf.memo }}
        onSubmit={handleSubmit}
        submitLabel="更新する"
      />
      <ShelfDeleteButton onDelete={handleDelete} />
      <Link href="/shelves">
        <button type="button" className="button">一覧に戻る</button>
      </Link>
    </div>
  );
}

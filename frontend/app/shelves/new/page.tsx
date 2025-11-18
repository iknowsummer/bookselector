"use client";

import { useRouter } from "next/navigation";
import Link from "next/link";
import { ShelfForm } from "@/app/shelves/_components/ShelfForm";
import { createShelf } from "@/lib/api/shelves";

export default function NewShelfPage() {
  const router = useRouter();

  const handleSubmit = async (data: { name: string; memo: string | null }) => {
    await createShelf(data);
    router.push("/shelves");
  };

  return (
    <div className="container">
      <h2>棚の新規登録</h2>
      <ShelfForm onSubmit={handleSubmit} submitLabel="登録する" />
      <Link href="/shelves">
        <button type="button">一覧に戻る</button>
      </Link>
    </div>
  );
}

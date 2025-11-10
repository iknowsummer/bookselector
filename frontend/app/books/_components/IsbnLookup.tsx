"use client";

import { useState, ChangeEvent } from "react";
import Image from "next/image";
import { lookupBookByIsbn } from "@/lib/api/books";

type IsbnLookupProps = {
  isbn: string | null;
  onIsbnChange: (isbn: string) => void;
  onBookInfoFetched: (bookInfo: {
    title: string;
    author: string | null;
    description: string | null;
    image_url: string | null;
  }) => void;
  imageUrl?: string | null;
};

export default function IsbnLookup({
  isbn,
  onIsbnChange,
  onBookInfoFetched,
  imageUrl,
}: IsbnLookupProps) {
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");

  const handleIsbnChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // 空文字列 or 数字のみを許可
    if (value === "" || /^[0-9]+$/.test(value)) {
      onIsbnChange(value);
      // 入力中はエラーをクリア
      if (lookupError) {
        setLookupError("");
      }
    }
  };

  const handleIsbnLookup = async () => {
    if (!isbn || isbn.length !== 13) {
      setLookupError("ISBNは13桁で入力してください");
      return;
    }

    setIsLookingUp(true);
    setLookupError("");

    try {
      const bookInfo = await lookupBookByIsbn(isbn);
      onBookInfoFetched({
        title: bookInfo.title,
        author: bookInfo.author,
        description: bookInfo.description,
        image_url: bookInfo.image_url,
      });
    } catch (err) {
      if (err instanceof Error) {
        setLookupError(err.message);
      } else {
        setLookupError("書籍情報の取得に失敗しました");
      }
    } finally {
      setIsLookingUp(false);
    }
  };

  return (
    <>
      <div style={{ display: "flex", gap: "8px" }}>
        <input
          type="text"
          name="isbn"
          value={isbn ?? ""}
          onChange={handleIsbnChange}
          placeholder="9784XXXXXXXXX"
          maxLength={13}
          pattern="[0-9]*"
          style={{ flex: 1 }}
        />
        <button
          type="button"
          onClick={handleIsbnLookup}
          disabled={isLookingUp || !isbn || isbn.length !== 13}
        >
          {isLookingUp ? "取得中..." : "情報取得"}
        </button>
      </div>
      {imageUrl && (
        <div style={{ marginTop: "12px" }}>
          <Image
            src={imageUrl}
            alt="書籍のサムネイル"
            width={128}
            height={192}
            style={{
              maxWidth: "128px",
              maxHeight: "192px",
              border: "1px solid #ddd",
              borderRadius: "4px",
              objectFit: "contain",
            }}
          />
        </div>
      )}
    </>
  );
}

"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { lookupBookByIsbn } from "@/lib/api/lookup";
import type { BookFormData } from "@/types/book";

export default function IsbnInputPage() {
  const router = useRouter();
  const [isbn, setIsbn] = useState<string>("");
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");

  const handleIsbnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // 空文字列 or 数字のみを許可
    if (value === "" || /^[0-9]+$/.test(value)) {
      setIsbn(value);
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

      // 取得した書籍情報をURLパラメータとして渡す
      const params = new URLSearchParams({
        isbn: isbn,
        title: bookInfo.title || "",
        author: bookInfo.author || "",
        description: bookInfo.description || "",
        image_url: bookInfo.image_url || "",
      });

      router.push(`/books/new/manual?${params.toString()}`);
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

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && isbn && isbn.length === 13) {
      handleIsbnLookup();
    }
  };

  const handleCancel = () => {
    router.push("/books/new");
  };

  return (
    <div className="container">
      <h2>ISBNから登録</h2>

      <div className="isbn-input-form">
        <div className="form-group">
          <label>ISBN</label>
          <p style={{ fontSize: "14px", color: "#666", marginBottom: "8px" }}>
            ISBNを入力すると、書籍情報を自動取得できます
          </p>
          <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
            <input
              type="text"
              value={isbn}
              onChange={handleIsbnChange}
              onKeyPress={handleKeyPress}
              placeholder="9784XXXXXXXXX"
              maxLength={13}
              pattern="[0-9]*"
              style={{ flex: 1 }}
              autoFocus
            />
            <button
              type="button"
              onClick={handleIsbnLookup}
              disabled={isLookingUp || !isbn || isbn.length !== 13}
            >
              {isLookingUp ? "取得中..." : "情報取得"}
            </button>
          </div>
          {lookupError && <div className="error-message">{lookupError}</div>}
        </div>

        <div style={{ marginTop: "24px" }}>
          <button type="button" onClick={handleCancel}>
            戻る
          </button>
        </div>
      </div>
    </div>
  );
}

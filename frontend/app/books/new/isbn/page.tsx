"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { lookupBookByIsbn } from "@/lib/api/lookup";
import IsbnInput, {
  cleanIsbn,
  isValidIsbn,
} from "@/app/books/_components/IsbnInput";

export default function IsbnInputPage() {
  const router = useRouter();
  const [isbn, setIsbn] = useState<string>("");
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");

  const handleIsbnChange = (value: string) => {
    setIsbn(value);
    if (lookupError) {
      setLookupError("");
    }
  };

  const handleIsbnLookup = async () => {
    // ハイフンを除去して13桁チェック
    if (!isValidIsbn(isbn)) {
      setLookupError("ISBNは13桁で入力してください");
      return;
    }

    const cleanedIsbn = cleanIsbn(isbn);

    setIsLookingUp(true);
    setLookupError("");

    try {
      const bookInfo = await lookupBookByIsbn(cleanedIsbn);

      // 取得した書籍情報をURLパラメータとして渡す
      const params = new URLSearchParams({
        isbn: cleanedIsbn,
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

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    // ハイフンを除去して13桁チェック
    if (e.key === "Enter" && isValidIsbn(isbn)) {
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
          <p className="helper-text">
            ISBNを入力すると、書籍情報を自動取得できます
          </p>
          <div className="input-row">
            <div className="input-wrapper" onKeyDown={handleKeyDown}>
              <IsbnInput value={isbn} onChange={handleIsbnChange} autoFocus />
            </div>
            <button
              type="button"
              onClick={handleIsbnLookup}
              disabled={isLookingUp || !isValidIsbn(isbn)}
              className="button"
            >
              {isLookingUp ? "取得中..." : "情報取得"}
            </button>
          </div>
          {lookupError && <div className="error-message">{lookupError}</div>}
        </div>

        <div className="back-button-container">
          <button type="button" onClick={handleCancel} className="button">
            戻る
          </button>
        </div>
      </div>
    </div>
  );
}

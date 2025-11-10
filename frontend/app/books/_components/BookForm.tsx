"use client";

import { useState, FormEvent, ChangeEvent, useEffect } from "react";
import Link from "next/link";
import type { BookFormData } from "@/types/book";
import { lookupBookByIsbn } from "@/lib/api/books";

type BookFormProps = {
  initialData?: BookFormData;
  onSubmit: (data: BookFormData) => Promise<void>;
  submitLabel: string;
  cancelHref: string;
  isLoading?: boolean;
  isEditMode?: boolean;
};

export default function BookForm({
  initialData = { title: "", author: "", description: "", isbn: "", image_url: "", note: "" },
  onSubmit,
  submitLabel,
  cancelHref,
  isLoading = false,
  isEditMode = false,
}: BookFormProps) {
  const [formData, setFormData] = useState<BookFormData>(initialData);
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isbnError, setIsbnError] = useState<string>("");
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");

  useEffect(() => {
    if (isEditMode) {
      setFormData(initialData);
    }
  }, [isEditMode, initialData]);

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleIsbnChange = (e: ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // 空文字列 or 数字のみを許可
    if (value === "" || /^[0-9]+$/.test(value)) {
      setFormData((prev) => ({
        ...prev,
        isbn: value,
      }));
      // 入力中はエラーをクリア
      if (isbnError) {
        setIsbnError("");
      }
      if (lookupError) {
        setLookupError("");
      }
    }
  };

  const handleIsbnLookup = async () => {
    if (!formData.isbn || formData.isbn.length !== 13) {
      setLookupError("ISBNは13桁で入力してください");
      return;
    }

    setIsLookingUp(true);
    setLookupError("");

    try {
      const bookInfo = await lookupBookByIsbn(formData.isbn);
      setFormData((prev) => ({
        ...prev,
        title: bookInfo.title,
        author: bookInfo.author,
        description: bookInfo.description,
        image_url: bookInfo.image_url,
      }));
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

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsbnError("");

    // ISBNバリデーション：入力されている場合は13桁かチェック
    if (formData.isbn && formData.isbn.length !== 13) {
      setIsbnError("ISBNは13桁で入力してください");
      return;
    }

    setIsSubmitting(true);

    try {
      await onSubmit(formData);
    } catch (err) {
      setError(`エラー: ${err}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="container">読み込み中...</div>;
  }

  return (
    <form onSubmit={handleSubmit} className="book-form">
      <div className="form-group">
        <label>タイトル *</label>
        <input
          type="text"
          name="title"
          value={formData.title}
          onChange={handleChange}
          required
        />
      </div>

      <div className="form-group">
        <label>著者</label>
        <input
          type="text"
          name="author"
          value={formData.author ?? ""}
          onChange={handleChange}
        />
      </div>

      <div className="form-group">
        <label>説明</label>
        <textarea
          name="description"
          value={formData.description ?? ""}
          onChange={handleChange}
          rows={4}
        />
      </div>

      <div className="form-group">
        <label>ISBN</label>
        <div style={{ display: "flex", gap: "8px" }}>
          <input
            type="text"
            name="isbn"
            value={formData.isbn ?? ""}
            onChange={handleIsbnChange}
            placeholder="9784XXXXXXXXX"
            maxLength={13}
            pattern="[0-9]*"
            style={{ flex: 1 }}
          />
          <button
            type="button"
            onClick={handleIsbnLookup}
            disabled={isLookingUp || !formData.isbn || formData.isbn.length !== 13}
          >
            {isLookingUp ? "取得中..." : "情報取得"}
          </button>
        </div>
        {isbnError && <div className="error-message">{isbnError}</div>}
        {lookupError && <div className="error-message">{lookupError}</div>}
        {formData.image_url && (
          <div style={{ marginTop: "12px" }}>
            <img
              src={formData.image_url}
              alt="書籍のサムネイル"
              style={{
                maxWidth: "128px",
                maxHeight: "192px",
                border: "1px solid #ddd",
                borderRadius: "4px",
              }}
            />
          </div>
        )}
      </div>

      <div className="form-group">
        <label>メモ</label>
        <textarea
          name="note"
          value={formData.note ?? ""}
          onChange={handleChange}
          rows={4}
        />
      </div>

      {error && <div className="error-message">{error}</div>}

      <div className="form-actions">
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? `${submitLabel}中...` : submitLabel}
        </button>
        <Link href={cancelHref}>
          <button type="button">キャンセル</button>
        </Link>
      </div>
    </form>
  );
}

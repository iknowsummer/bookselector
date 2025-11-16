"use client";

import { useState, FormEvent, ChangeEvent, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import IsbnInput, { cleanIsbn } from "./IsbnInput";
import type { BookFormData } from "@/types/book";

type BookFormProps = {
  initialData?: BookFormData;
  onSubmit: (data: BookFormData) => Promise<void>;
  submitLabel: string;
  cancelHref: string;
  isLoading?: boolean;
  onBackToIsbnInput?: () => void;
};

export default function BookForm({
  initialData = { title: "", author: "", description: "", isbn: "", image_url: "", note: "" },
  onSubmit,
  submitLabel,
  cancelHref,
  isLoading = false,
  onBackToIsbnInput,
}: BookFormProps) {
  const [formData, setFormData] = useState<BookFormData>(initialData);
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    setFormData(initialData);
  }, [initialData]);

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleIsbnChange = (value: string) => {
    setFormData((prev) => ({
      ...prev,
      isbn: value,
    }));
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

    setIsSubmitting(true);

    try {
      // ISBNのハイフンを除去してから送信
      const submittedData = {
        ...formData,
        isbn: formData.isbn ? cleanIsbn(formData.isbn) : null,
      };
      await onSubmit(submittedData);
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
        <IsbnInput
          value={formData.isbn ?? ""}
          onChange={handleIsbnChange}
        />
      </div>

      {formData.image_url && (
        <div className="form-group">
          <label>サムネイル</label>
          <div style={{ marginTop: "8px" }}>
            <Image
              src={formData.image_url}
              alt={formData.title || "書籍の画像"}
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
        </div>
      )}

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

      {onBackToIsbnInput && (
        <div style={{ textAlign: "center", margin: "24px 0" }}>
          <button type="button" onClick={onBackToIsbnInput}>
            ISBNで情報取得
          </button>
        </div>
      )}

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

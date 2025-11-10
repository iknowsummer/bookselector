"use client";

import { useState, FormEvent, ChangeEvent, useEffect } from "react";
import Link from "next/link";
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

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");

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
        <input
          type="text"
          name="isbn"
          value={formData.isbn ?? ""}
          onChange={handleChange}
          placeholder="9784XXXXXXXXX"
          maxLength={13}
        />
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

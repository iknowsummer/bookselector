"use client";

import { useState, FormEvent, ChangeEvent } from "react";
import Link from "next/link";

export type BookFormData = {
  title: string;
  author: string;
  description: string;
  isbn: string;
  note: string;
};

type BookFormProps = {
  initialData?: BookFormData;
  onSubmit: (data: BookFormData) => Promise<void>;
  submitLabel: string;
  cancelHref: string;
  isLoading?: boolean;
};

export default function BookForm({
  initialData = { title: "", author: "", description: "", isbn: "", note: "" },
  onSubmit,
  submitLabel,
  cancelHref,
  isLoading = false,
}: BookFormProps) {
  const [formData, setFormData] = useState<BookFormData>(initialData);
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

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
          value={formData.author}
          onChange={handleChange}
        />
      </div>

      <div className="form-group">
        <label>説明</label>
        <textarea
          name="description"
          value={formData.description}
          onChange={handleChange}
          rows={4}
        />
      </div>

      <div className="form-group">
        <label>ISBN</label>
        <input
          type="text"
          name="isbn"
          value={formData.isbn}
          onChange={handleChange}
          placeholder="9784XXXXXXXXX"
        />
      </div>

      <div className="form-group">
        <label>メモ</label>
        <textarea
          name="note"
          value={formData.note}
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

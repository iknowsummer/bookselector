"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { createBook } from "@/lib/api/books";
import Link from "next/link";

export default function NewBookPage() {
  const router = useRouter();
  const [formData, setFormData] = useState({
    title: "",
    author: "",
    description: "",
    note: "",
  });
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);

    try {
      await createBook({
        title: formData.title,
        author: formData.author || null,
        description: formData.description || null,
        note: formData.note || null,
      });
      router.push("/books");
    } catch (err) {
      setError(`登録エラー: ${err}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="container">
      <h2>書籍登録</h2>
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
            {isSubmitting ? "登録中..." : "登録"}
          </button>
          <Link href="/books">
            <button type="button">キャンセル</button>
          </Link>
        </div>
      </form>
    </div>
  );
}

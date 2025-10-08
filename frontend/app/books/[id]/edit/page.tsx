"use client";

import { useEffect, useState } from "react";
import { useRouter, useParams } from "next/navigation";
import { fetchBook, updateBook } from "@/lib/api/books";
import Link from "next/link";

export default function EditBookPage() {
  const router = useRouter();
  const params = useParams();
  const [formData, setFormData] = useState({
    title: "",
    author: "",
    description: "",
    note: "",
  });
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const getData = async () => {
      try {
        const id = Number(params.id);
        const book = await fetchBook(id);
        setFormData({
          title: book.title,
          author: book.author || "",
          description: book.description || "",
          note: book.note || "",
        });
      } catch (err) {
        setError(`書籍の取得に失敗しました: ${err}`);
      } finally {
        setIsLoading(false);
      }
    };
    getData();
  }, [params.id]);

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
      const id = Number(params.id);
      await updateBook(id, {
        title: formData.title,
        author: formData.author || null,
        description: formData.description || null,
        note: formData.note || null,
      });
      router.push(`/books/${id}`);
    } catch (err) {
      setError(`更新エラー: ${err}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  if (isLoading) {
    return <div className="container">読み込み中...</div>;
  }

  if (error && !formData.title) {
    return (
      <div className="container">
        <div className="error">エラー: {error}</div>
        <Link href="/books">
          <button>書籍一覧に戻る</button>
        </Link>
      </div>
    );
  }

  return (
    <div className="container">
      <h2>書籍編集</h2>
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
            {isSubmitting ? "更新中..." : "更新"}
          </button>
          <Link href={`/books/${params.id}`}>
            <button type="button">キャンセル</button>
          </Link>
        </div>
      </form>
    </div>
  );
}

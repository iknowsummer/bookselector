"use client";

import { useState, FormEvent, ChangeEvent, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import IsbnInput, { cleanIsbn } from "./IsbnInput";
import type { BookFormData } from "@/types/book";
import type { Shelf } from "@/types/shelf";
import { fetchShelves } from "@/lib/api/shelves";
import { createBook } from "@/lib/api/books";
import { createUserBook, updateUserBook } from "@/lib/api/userBooks";
import {
  formDataToBookCreate,
  formDataToUserBookCreate,
  formDataToUserBookUpdate,
} from "@/lib/api/bookTransformers";
import styles from "./BookForm.module.css";

type BookFormProps = {
  initialData?: BookFormData;
  bookId?: number;
  submitLabel: string;
  isLoading?: boolean;
  onBackToIsbnInput?: () => void;
  redirectTo?: string;
};

export default function BookForm({
  initialData = { title: "", author: "", description: "", isbn: "", image_url: "", note: "", shelf_id: null },
  bookId,
  submitLabel,
  isLoading = false,
  onBackToIsbnInput,
  redirectTo = "/books",
}: BookFormProps) {
  const router = useRouter();
  const [formData, setFormData] = useState<BookFormData>(initialData);
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [shelves, setShelves] = useState<Shelf[]>([]);
  const [shelvesLoading, setShelvesLoading] = useState(false);

  // 棚一覧を取得
  useEffect(() => {
    const loadShelves = async () => {
      setShelvesLoading(true);
      try {
        const data = await fetchShelves();
        setShelves(data);
      } catch (err) {
        console.error("棚一覧の取得に失敗しました:", err);
      } finally {
        setShelvesLoading(false);
      }
    };
    loadShelves();
  }, []);

  useEffect(() => {
    setFormData(initialData);
  }, [initialData]);

  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value === "" ? null : name === "shelf_id" ? Number(value) : value,
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

      // bookIdの有無で新規/編集を判別
      if (bookId !== undefined) {
        // 編集処理（user_booksのみ）
        await updateUserBook(bookId, formDataToUserBookUpdate(submittedData));
      } else {
        // 新規作成処理（books -> user_books）
        const createdBook = await createBook(formDataToBookCreate(submittedData));
        await createUserBook(formDataToUserBookCreate(submittedData, createdBook.id));
      }

      // 送信成功後にリダイレクト
      router.push(redirectTo);
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
          readOnly
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
          readOnly
        />
      </div>

      <div className="form-group">
        <label>説明</label>
        <textarea
          name="description"
          value={formData.description ?? ""}
          onChange={handleChange}
          readOnly
          rows={4}
        />
      </div>

      <div className="form-group">
        <label>ISBN</label>
        <IsbnInput
          value={formData.isbn ?? ""}
          onChange={handleIsbnChange}
          readOnly
        />
      </div>

      <div className="form-group">
        <label>棚</label>
        <select
          name="shelf_id"
          value={formData.shelf_id ?? ""}
          onChange={handleChange}
          disabled={shelvesLoading}
        >
          <option value="">棚なし</option>
          {shelves.map((shelf) => (
            <option key={shelf.id} value={shelf.id}>
              {shelf.name}
            </option>
          ))}
        </select>
        {shelvesLoading && <span className={styles["loading-text"]}>読み込み中...</span>}
      </div>

      {formData.image_url && (
        <div className="form-group">
          <label>サムネイル</label>
          <div className={styles["thumbnail-container"]}>
            <Image
              src={formData.image_url}
              alt={formData.title || "書籍の画像"}
              width={128}
              height={192}
              className={styles["thumbnail-image"]}
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
        <div className={styles["isbn-button-container"]}>
          <button type="button" onClick={onBackToIsbnInput} className="button">
            ISBNで情報取得
          </button>
        </div>
      )}

      <div className="form-actions">
        <button type="submit" disabled={isSubmitting} className="button">
          {isSubmitting ? `${submitLabel}中...` : submitLabel}
        </button>
        <button type="button" onClick={() => router.back()} className="button">
          キャンセル
        </button>
      </div>
    </form>
  );
}

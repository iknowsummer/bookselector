"use client";

import { useState } from "react";
import type { ShelfFormData } from "@/types/shelf";

type Props = {
  initialData?: ShelfFormData;
  onSubmit: (data: ShelfFormData) => Promise<void>;
  submitLabel: string;
};

export function ShelfForm({ initialData, onSubmit, submitLabel }: Props) {
  const [formData, setFormData] = useState<ShelfFormData>(
    initialData ?? {
      name: "",
      memo: "",
    }
  );
  const [error, setError] = useState<string>("");
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);

  const handleChange = (
    e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>
  ) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setError("");
    setIsSubmitting(true);
    try {
      if (!formData.name) {
        throw new Error("棚名は必須です");
      }
      await onSubmit({
        name: formData.name,
        memo: formData.memo ?? "",
      });
    } catch (err) {
      setError(`${err}`);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form className="shelf-form" onSubmit={handleSubmit}>
      <label>
        棚の名称
        <input
          type="text"
          name="name"
          value={formData.name}
          onChange={handleChange}
          required
        />
      </label>
      <label>
        メモ
        <textarea
          name="memo"
          value={formData.memo ?? ""}
          onChange={handleChange}
          rows={4}
        />
      </label>
      {error && <div className="error">エラー: {error}</div>}
      <div className="form-actions">
        <button type="submit" disabled={isSubmitting}>
          {isSubmitting ? "送信中..." : submitLabel}
        </button>
      </div>
    </form>
  );
}

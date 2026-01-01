"use client";

import { ChangeEvent } from "react";

type IsbnInputProps = {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  required?: boolean;
  autoFocus?: boolean;
  name?: string;
  readOnly?: boolean;
};

export default function IsbnInput({
  value,
  onChange,
  placeholder = "978-4-XXXXXXXXX",
  required = false,
  autoFocus = false,
  name = "isbn",
  readOnly = false,
}: IsbnInputProps) {
  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    const inputValue = e.target.value;
    // 空文字列 or 数字とハイフンを許可
    if (inputValue === "" || /^[0-9-]+$/.test(inputValue)) {
      onChange(inputValue);
    }
  };

  return (
    <input
      type="text"
      name={name}
      value={value}
      onChange={handleChange}
      placeholder={placeholder}
      pattern="[0-9-]*"
      inputMode="numeric"
      required={required}
      autoFocus={autoFocus}
      readOnly={readOnly}
    />
  );
}

/**
 * ハイフンを除去してクリーンなISBNを取得するユーティリティ関数
 */
export function cleanIsbn(isbn: string): string {
  return isbn.replace(/-/g, "");
}

/**
 * ISBNが有効な13桁かチェックするユーティリティ関数
 */
export function isValidIsbn(isbn: string): boolean {
  const cleaned = cleanIsbn(isbn);
  return cleaned.length === 13 && /^[0-9]+$/.test(cleaned);
}

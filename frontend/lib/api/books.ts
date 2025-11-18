import type { Book } from "@/types/book";
import { getApiBaseUrl } from "./client";

export const fetchApiStatus = async (): Promise<string> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(apiBaseUrl);
  if (!res.ok) {
    throw new Error("APIの取得に失敗しました");
  }
  return await res.text();
};

export const fetchRandomBooks = async (): Promise<Book[]> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/books/random`);
  if (!res.ok) {
    throw new Error("書籍情報の取得に失敗しました");
  }
  return await res.json();
};

export const fetchBooks = async (): Promise<Book[]> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/books`);
  if (!res.ok) {
    throw new Error("書籍情報の取得に失敗しました");
  }
  return await res.json();
};

export const fetchLatestBooks = async (limit: number): Promise<Book[]> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(
    `${apiBaseUrl}/books?limit=${limit}&order_by=created_at&order=desc`
  );
  if (!res.ok) {
    throw new Error("最新書籍情報の取得に失敗しました");
  }
  return await res.json();
};

export const createBook = async (
  bookData: Omit<Book, "id">
): Promise<Book> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/books`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(bookData),
  });
  if (!res.ok) {
    throw new Error("書籍の登録に失敗しました");
  }
  return await res.json();
};

export const fetchBook = async (id: number): Promise<Book> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/books/${id}`);
  if (!res.ok) {
    if (res.status === 404) {
      throw new Error("書籍が見つかりません");
    }
    throw new Error("書籍情報の取得に失敗しました");
  }
  return await res.json();
};

export const updateBook = async (
  id: number,
  bookData: Partial<Omit<Book, "id" | "status" | "created_at">>
): Promise<Book> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/books/${id}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(bookData),
  });
  if (!res.ok) {
    throw new Error("書籍の更新に失敗しました");
  }
  return await res.json();
};

export const deleteBook = async (id: number): Promise<void> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/books/${id}`, {
    method: "DELETE",
  });
  if (!res.ok) {
    throw new Error("書籍の削除に失敗しました");
  }
};

export const updateBookStatus = async (
  id: number,
  status: "unread" | "picked" | "read"
): Promise<Book> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/books/${id}/status`, {
    method: "PATCH",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ status }),
  });
  if (!res.ok) {
    throw new Error("書籍のステータスの更新に失敗しました");
  }
  return await res.json();
};


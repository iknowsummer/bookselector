import type { Book } from "@/types/book";

const getApiBaseUrl = () => {
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

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
  const res = await fetch(`${apiBaseUrl}/books/random/`);
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
  const res = await fetch(`${apiBaseUrl}/books?id=${id}`);
  if (!res.ok) {
    throw new Error("書籍情報の取得に失敗しました");
  }
  const books = await res.json();
  if (books.length === 0) {
    throw new Error("書籍が見つかりません");
  }
  return books[0];
};

export const updateBook = async (
  id: number,
  bookData: Omit<Book, "id">
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

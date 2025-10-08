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

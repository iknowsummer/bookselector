import { getApiBaseUrl } from "./client";
import type { UserBook, UserBookCreatePayload, UserBookUpdatePayload } from "@/types/userBook";

export const createUserBook = async (
  payload: UserBookCreatePayload
): Promise<UserBook> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/user-books`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error("書籍メモの登録に失敗しました");
  }
  return await res.json();
};

export const updateUserBook = async (
  bookId: number,
  payload: UserBookUpdatePayload
): Promise<UserBook> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/user-books/${bookId}`, {
    method: "PUT",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    throw new Error("書籍メモの更新に失敗しました");
  }
  return await res.json();
};

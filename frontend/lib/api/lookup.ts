import type { GoogleBooksResponse } from "@/types/lookup";
import { getApiBaseUrl } from "./client";
import { authenticatedFetch } from "./authenticatedFetch";

export const lookupBookByIsbn = async (
  isbn: string
): Promise<GoogleBooksResponse> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await authenticatedFetch(`${apiBaseUrl}/lookup/isbn/${isbn}`);
  if (!res.ok) {
    if (res.status === 400) {
      throw new Error("ISBNの形式が正しくありません(13桁の数字を入力してください)");
    }
    if (res.status === 404) {
      throw new Error("書籍情報が見つかりませんでした");
    }
    throw new Error("書籍情報の取得に失敗しました");
  }
  return await res.json();
};

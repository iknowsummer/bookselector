import type { GoogleBooksResponse } from "@/types/lookup";

const getApiBaseUrl = () => {
  const url = process.env.NEXT_PUBLIC_API_URL;
  if (!url) {
    throw new Error("NEXT_PUBLIC_API_URL環境変数が設定されていません");
  }
  return url;
};

export const lookupBookByIsbn = async (
  isbn: string
): Promise<GoogleBooksResponse> => {
  const apiBaseUrl = getApiBaseUrl();
  const res = await fetch(`${apiBaseUrl}/lookup/isbn/${isbn}`);
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

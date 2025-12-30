import { useState, useCallback, useRef } from "react";
import { lookupBookByIsbn } from "@/lib/api/lookup";

export interface BookLookupResult {
  title: string;
  author: string;
  description: string;
  image_url: string;
}

export function useBookLookup() {
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");
  const [failedIsbn, setFailedIsbn] = useState<string>("");
  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const clearError = useCallback(() => {
    setLookupError("");
    setFailedIsbn("");
  }, []);

  const lookupBook = useCallback(
    async (isbn: string): Promise<BookLookupResult> => {
      // 前回エラーになったISBNと同じ場合はスキップ(無限ループ防止)
      if (isbn === failedIsbn) {
        const error = "このISBNは取得に失敗しました。別のバーコードを試してください。";
        setLookupError(error);
        throw new Error(error);
      }

      setLookupError("");

      try {
        setIsLookingUp(true);
        const bookInfo = await lookupBookByIsbn(isbn);

        return {
          title: bookInfo.title || "",
          author: bookInfo.author || "",
          description: bookInfo.description || "",
          image_url: bookInfo.image_url || "",
        };
      } catch (err) {
        setFailedIsbn(isbn);
        const errorMessage =
          err instanceof Error ? err.message : "書籍情報の取得に失敗しました";
        setLookupError(errorMessage);

        // エラーメッセージを5秒後に自動クリア
        if (errorTimeoutRef.current) {
          clearTimeout(errorTimeoutRef.current);
        }
        errorTimeoutRef.current = setTimeout(() => {
          clearError();
        }, 5000);

        throw err;
      } finally {
        setIsLookingUp(false);
      }
    },
    [failedIsbn, clearError]
  );

  // クリーンアップ用関数（useEffect内で使用）
  const cleanup = useCallback(() => {
    if (errorTimeoutRef.current) {
      clearTimeout(errorTimeoutRef.current);
    }
  }, []);

  return {
    lookupBook,
    isLookingUp,
    lookupError,
    clearError,
    cleanup,
  };
}

"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { lookupBookByIsbn } from "@/lib/api/lookup";
import BarcodeScanner from "@/app/books/_components/BarcodeScanner";

export default function ScanPage() {
  const router = useRouter();
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");
  const [failedIsbn, setFailedIsbn] = useState<string>(""); // エラーになったISBNを記録

  const handleScanSuccess = useCallback(async (scannedIsbn: string) => {
    // 前回エラーになったISBNと同じ場合はスキップ（無限ループ防止）
    if (scannedIsbn === failedIsbn) {
      setLookupError("このISBNは取得に失敗しました。別のバーコードを試してください。");
      return;
    }

    setLookupError("");

    // スキャン成功後、自動的に情報取得
    try {
      setIsLookingUp(true);
      const bookInfo = await lookupBookByIsbn(scannedIsbn);

      // 取得した書籍情報をURLパラメータとして渡す
      const params = new URLSearchParams({
        isbn: scannedIsbn,
        title: bookInfo.title || "",
        author: bookInfo.author || "",
        description: bookInfo.description || "",
        image_url: bookInfo.image_url || "",
      });

      router.push(`/books/new/manual?${params.toString()}`);
    } catch (err) {
      setFailedIsbn(scannedIsbn); // 失敗したISBNを記録
      if (err instanceof Error) {
        setLookupError(err.message);
      } else {
        setLookupError("書籍情報の取得に失敗しました");
      }
      setIsLookingUp(false);

      // エラーメッセージを5秒後に自動クリア
      setTimeout(() => {
        setLookupError("");
      }, 5000);
    }
  }, [router, failedIsbn]);

  const handleScanError = useCallback((error: string) => {
    setLookupError(error);
  }, []);

  const handleScannerClose = () => {
    router.push("/books/new");
  };

  return (
    <div className="container">
      {isLookingUp ? (
        <div className="loading-container">
          <p>書籍情報を取得中...</p>
        </div>
      ) : (
        <>
          {lookupError && (
            <div className="error-toast">
              {lookupError}
            </div>
          )}
          <BarcodeScanner
            onScan={handleScanSuccess}
            onClose={handleScannerClose}
            onError={handleScanError}
          />
        </>
      )}
    </div>
  );
}

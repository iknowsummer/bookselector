"use client";

import { useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import { lookupBookByIsbn } from "@/lib/api/lookup";
import BarcodeScanner from "@/app/books/_components/BarcodeScanner";

export default function ScanPage() {
  const router = useRouter();
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");

  const handleScanSuccess = useCallback(async (scannedIsbn: string) => {
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
      if (err instanceof Error) {
        setLookupError(err.message);
      } else {
        setLookupError("書籍情報の取得に失敗しました");
      }
      setIsLookingUp(false);
    }
  }, [router]);

  const handleScanError = useCallback((error: string) => {
    setLookupError(error);
  }, []);

  const handleScannerClose = () => {
    router.push("/books/new");
  };

  return (
    <div className="container">
      {isLookingUp ? (
        <div style={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          height: "100vh",
          flexDirection: "column",
          gap: "16px"
        }}>
          <p>書籍情報を取得中...</p>
        </div>
      ) : (
        <>
          {lookupError && (
            <div style={{
              position: "fixed",
              top: "80px",
              left: "50%",
              transform: "translateX(-50%)",
              zIndex: 10000,
              backgroundColor: "#f44336",
              color: "white",
              padding: "12px 24px",
              borderRadius: "4px",
              boxShadow: "0 2px 8px rgba(0,0,0,0.2)"
            }}>
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

"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useBarcodeScanner } from "@/hooks/useBarcodeScanner";
import { useBookLookup } from "@/hooks/useBookLookup";
import { BarcodeScanner } from "./_components/BarcodeScanner";
import { AlternativeButtons } from "./_components/AlternativeButtons";
import styles from "./NewBookPage.module.css";

export default function NewBookPage() {
  const router = useRouter();
  const [isScanning, setIsScanning] = useState(true);
  const [scanError, setScanError] = useState<string>("");

  const { lookupBook, isLookingUp, lookupError, cleanup } = useBookLookup();

  const handleScanSuccess = async (isbn: string) => {
    setIsScanning(false);

    try {
      const bookInfo = await lookupBook(isbn);

      const params = new URLSearchParams({
        isbn: isbn,
        title: bookInfo.title,
        author: bookInfo.author,
        description: bookInfo.description,
        image_url: bookInfo.image_url,
      });

      router.push(`/books/new/manual?${params.toString()}`);
    } catch {
      // エラーは useBookLookup 内で処理済み
      setIsScanning(true);
    }
  };

  const handleScanError = (error: string) => {
    setScanError(error);
  };

  const handleScanTimeout = () => {
    setScanError("スキャナーを再起動します...");
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  };

  const { videoRef } = useBarcodeScanner({
    onSuccess: handleScanSuccess,
    onError: handleScanError,
    onTimeout: handleScanTimeout,
  });

  // クリーンアップ
  useEffect(() => {
    return () => {
      cleanup();
    };
  }, [cleanup]);

  // エラー表示の統合（スキャンエラーとルックアップエラー）
  const displayError = scanError || lookupError;

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>書籍登録</h2>

      <BarcodeScanner
        videoRef={videoRef}
        isScanning={isScanning}
        isLookingUp={isLookingUp}
        error={displayError}
      />

      <AlternativeButtons />
    </div>
  );
}

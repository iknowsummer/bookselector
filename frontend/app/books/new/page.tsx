"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { BrowserMultiFormatReader, NotFoundException } from "@zxing/library";
import { lookupBookByIsbn } from "@/lib/api/lookup";
import styles from "./NewBookPage.module.css";

export default function NewBookPage() {
  const router = useRouter();
  const videoRef = useRef<HTMLVideoElement>(null);
  const codeReaderRef = useRef<BrowserMultiFormatReader | null>(null);
  const hasScannedRef = useRef(false);
  const errorTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const scanTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const [isScanning, setIsScanning] = useState(true);
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");
  const [failedIsbn, setFailedIsbn] = useState<string>("");

  const handleScanSuccess = useCallback(
    async (scannedIsbn: string) => {
      // スキャンタイムアウトのクリア
      if (scanTimeoutRef.current) {
        clearTimeout(scanTimeoutRef.current);
      }

      // 前回エラーになったISBNと同じ場合はスキップ(無限ループ防止)
      if (scannedIsbn === failedIsbn) {
        setLookupError(
          "このISBNは取得に失敗しました。別のバーコードを試してください。"
        );
        return;
      }

      setLookupError("");

      try {
        setIsLookingUp(true);
        const bookInfo = await lookupBookByIsbn(scannedIsbn);

        const params = new URLSearchParams({
          isbn: scannedIsbn,
          title: bookInfo.title || "",
          author: bookInfo.author || "",
          description: bookInfo.description || "",
          image_url: bookInfo.image_url || "",
        });

        router.push(`/books/new/manual?${params.toString()}`);
      } catch (err) {
        setFailedIsbn(scannedIsbn);
        if (err instanceof Error) {
          setLookupError(err.message);
        } else {
          setLookupError("書籍情報の取得に失敗しました");
        }
        setIsLookingUp(false);

        // エラーメッセージを5秒後に自動クリア
        if (errorTimeoutRef.current) {
          clearTimeout(errorTimeoutRef.current);
        }
        errorTimeoutRef.current = setTimeout(() => {
          setLookupError("");
          setFailedIsbn("");
        }, 5000);
      }
    },
    [router, failedIsbn]
  );

  const handleScanError = useCallback((error: string) => {
    setLookupError(error);
  }, []);

  const handleScanTimeout = useCallback(() => {
    const videoElement = videoRef.current;

    // ストリーム停止
    if (videoElement?.srcObject) {
      const stream = videoElement.srcObject as MediaStream;
      stream.getTracks().forEach((track) => track.stop());
    }
    if (codeReaderRef.current) {
      codeReaderRef.current.reset();
    }

    // メッセージ表示してリロード
    setLookupError("スキャナーを再起動します...");
    setTimeout(() => {
      window.location.reload();
    }, 1000);
  }, []);

  useEffect(() => {
    const codeReader = new BrowserMultiFormatReader();
    codeReaderRef.current = codeReader;
    const videoElement = videoRef.current;

    const startScanning = async () => {
      try {
        // カメラデバイスの取得
        const videoInputDevices = await codeReader.listVideoInputDevices();

        if (videoInputDevices.length === 0) {
          handleScanError("カメラが見つかりませんでした");
          return;
        }

        // 背面カメラを優先的に選択(モバイルの場合)
        const selectedDevice =
          videoInputDevices.find((device) =>
            device.label.toLowerCase().includes("back")
          ) || videoInputDevices[0];

        // スキャン開始
        await codeReader.decodeFromVideoDevice(
          selectedDevice.deviceId,
          videoRef.current!,
          (result, error) => {
            // 既にスキャン済みの場合は処理しない
            if (hasScannedRef.current) {
              return;
            }

            if (result) {
              const text = result.getText();
              // ISBN-13形式(978または979で始まる13桁の数字)のみ採用
              if (/^(978|979)\d{10}$/.test(text)) {
                hasScannedRef.current = true;
                setIsScanning(false);
                codeReader.reset();
                handleScanSuccess(text);
              }
            }

            if (error && !(error instanceof NotFoundException)) {
              console.error("Barcode scan error:", error);
            }
          }
        );

        // タイマー設定: 60秒後に自動リセット
        scanTimeoutRef.current = setTimeout(() => {
          handleScanTimeout();
        }, 60000);
      } catch (err) {
        console.error("Camera initialization error:", err);
        if (err instanceof Error) {
          if (err.name === "NotAllowedError") {
            handleScanError("カメラの権限が必要です");
          } else if (err.name === "NotFoundError") {
            handleScanError("カメラが見つかりませんでした");
          } else {
            handleScanError("カメラが利用できません");
          }
        } else {
          handleScanError("カメラが利用できません");
        }
      }
    };

    startScanning();

    // クリーンアップ
    return () => {
      // スキャンタイムアウトのクリア
      if (scanTimeoutRef.current) {
        clearTimeout(scanTimeoutRef.current);
      }

      // エラータイムアウトのクリア
      if (errorTimeoutRef.current) {
        clearTimeout(errorTimeoutRef.current);
      }

      // MediaStreamの明示的な停止
      if (videoElement?.srcObject) {
        const stream = videoElement.srcObject as MediaStream;
        stream.getTracks().forEach((track) => track.stop());
      }

      // コードリーダーのリセット
      if (codeReaderRef.current) {
        codeReaderRef.current.reset();
      }
    };
  }, [handleScanSuccess, handleScanError, handleScanTimeout]);

  return (
    <div className={styles.container}>
      <h2 className={styles.title}>書籍登録</h2>

      {/* Scanner Area - Top Half */}
      <div className={styles["scanner-area"]}>
        {isLookingUp ? (
          <div className={styles["loading-overlay"]}>
            <p>書籍情報を取得中...</p>
          </div>
        ) : (
          <>
            {lookupError && (
              <div className={styles["error-toast"]}>{lookupError}</div>
            )}
            <video ref={videoRef} className={styles.video} playsInline />
            <div className={styles.overlay}>
              <div className={styles["guide-box"]}>
                <div className={styles["guide-text"]}>
                  バーコードをここに合わせてください
                </div>
              </div>
              {isScanning && <div className={styles.status}>スキャン中...</div>}
            </div>
          </>
        )}
      </div>

      {/* Alternative Methods - Bottom Half */}
      <div className={styles["alternatives-area"]}>
        <div className={styles["alternatives-buttons"]}>
          <Link href="/books/new/isbn">
            <button type="button" className={`button ${styles["alt-button"]}`}>
              ISBNで登録
            </button>
          </Link>
          <Link href="/books/new/manual">
            <button type="button" className={`button ${styles["alt-button"]}`}>
              手動で登録
            </button>
          </Link>
        </div>

        <div className="back-button-container">
          <Link href="/books">
            <button type="button" className="button">
              戻る
            </button>
          </Link>
        </div>
      </div>
    </div>
  );
}

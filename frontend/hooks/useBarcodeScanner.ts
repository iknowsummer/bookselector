import { useEffect, useRef, useCallback } from "react";
import { BrowserMultiFormatReader, NotFoundException } from "@zxing/library";

// ISBN-13形式の検証用正規表現（978または979で始まる13桁）
const ISBN13_REGEX = /^(978|979)\d{10}$/;

export interface UsBarcodeScannerOptions {
  onSuccess: (isbn: string) => void;
  onError: (error: string) => void;
  onTimeout: () => void;
  scanTimeoutMs?: number;
  frameSkip?: number; // フレームスキップ設定（デフォルト: 2）
}

export function useBarcodeScanner({
  onSuccess,
  onError,
  onTimeout,
  scanTimeoutMs = 60000,
  frameSkip = 2, // デフォルト: 2フレームに1回解析
}: UsBarcodeScannerOptions) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const codeReaderRef = useRef<BrowserMultiFormatReader | null>(null);
  const hasScannedRef = useRef(false);
  const scanTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const frameCountRef = useRef(0); // フレームカウンタ
  const lastErrorLogRef = useRef(0); // 最後のエラーログ時刻

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

    onTimeout();
  }, [onTimeout]);

  useEffect(() => {
    const codeReader = new BrowserMultiFormatReader();
    codeReaderRef.current = codeReader;
    const videoElement = videoRef.current;

    const startScanning = async () => {
      try {
        // カメラデバイスの取得
        const videoInputDevices = await codeReader.listVideoInputDevices();

        if (videoInputDevices.length === 0) {
          onError("カメラが見つかりませんでした");
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
            // フレームカウンタをインクリメント
            frameCountRef.current += 1;

            // フレームスキップ判定（frameSkip回に1回だけ処理）
            if (frameCountRef.current % frameSkip !== 0) {
              return;
            }

            // 既にスキャン済みの場合は処理しない
            if (hasScannedRef.current) {
              return;
            }

            if (result) {
              const text = result.getText();
              // ISBN-13形式の検証（定数化した正規表現を使用）
              if (ISBN13_REGEX.test(text)) {
                hasScannedRef.current = true;

                // スキャンタイムアウトのクリア
                if (scanTimeoutRef.current) {
                  clearTimeout(scanTimeoutRef.current);
                }

                codeReader.reset();
                onSuccess(text);
              }
            }

            // エラーログのスロットリング（1秒間隔）
            if (error && !(error instanceof NotFoundException)) {
              const now = Date.now();
              if (now - lastErrorLogRef.current > 1000) {
                console.error("Barcode scan error:", error);
                lastErrorLogRef.current = now;
              }
            }
          }
        );

        // タイマー設定: 指定時間後に自動リセット
        scanTimeoutRef.current = setTimeout(() => {
          handleScanTimeout();
        }, scanTimeoutMs);
      } catch (err) {
        console.error("Camera initialization error:", err);
        if (err instanceof Error) {
          if (err.name === "NotAllowedError") {
            onError("カメラの権限が必要です");
          } else if (err.name === "NotFoundError") {
            onError("カメラが見つかりませんでした");
          } else {
            onError("カメラが利用できません");
          }
        } else {
          onError("カメラが利用できません");
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
  }, [onSuccess, onError, handleScanTimeout, scanTimeoutMs, frameSkip]);

  return {
    videoRef,
  };
}

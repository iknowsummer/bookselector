"use client";

import { useEffect, useRef, useState } from "react";
import { BrowserMultiFormatReader, NotFoundException } from "@zxing/library";

interface BarcodeScannerProps {
  onScan: (isbn: string) => void;
  onClose: () => void;
  onError: (error: string) => void;
}

export default function BarcodeScanner({
  onScan,
  onClose,
  onError,
}: BarcodeScannerProps) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const [isScanning, setIsScanning] = useState(true);
  const codeReaderRef = useRef<BrowserMultiFormatReader | null>(null);
  const hasScannedRef = useRef(false); // スキャン完了フラグ

  useEffect(() => {
    const codeReader = new BrowserMultiFormatReader();
    codeReaderRef.current = codeReader;

    const startScanning = async () => {
      try {
        // カメラデバイスの取得
        const videoInputDevices = await codeReader.listVideoInputDevices();

        if (videoInputDevices.length === 0) {
          onError("カメラが見つかりませんでした");
          return;
        }

        // 背面カメラを優先的に選択（モバイルの場合）
        const selectedDevice = videoInputDevices.find(
          (device) => device.label.toLowerCase().includes("back")
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
              // ISBN-13形式（978または979で始まる13桁の数字）のみ採用
              // それ以外のバーコード（JANコード、ISBN-10など）は静かに無視
              if (/^(978|979)\d{10}$/.test(text)) {
                hasScannedRef.current = true; // スキャン完了フラグを立てる
                setIsScanning(false);
                // カメラを即座に停止
                codeReader.reset();
                onScan(text);
              }
              // ISBN-13以外は何もせず次のフレームを待つ
            }

            if (error && !(error instanceof NotFoundException)) {
              console.error("Barcode scan error:", error);
            }
          }
        );
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
      if (codeReaderRef.current) {
        codeReaderRef.current.reset();
      }
    };
  }, [onScan, onError]);

  const handleClose = () => {
    if (codeReaderRef.current) {
      codeReaderRef.current.reset();
    }
    onClose();
  };

  return (
    <div className="fixed inset-0 z-[9999] flex items-center justify-center bg-black">
      {/* カメラプレビュー */}
      <video
        ref={videoRef}
        className="w-full h-full object-cover"
        playsInline
      />

      {/* オーバーレイとガイド */}
      <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
        {/* スキャンガイド */}
        <div className="relative w-64 h-40 border-4 border-white rounded-lg shadow-lg">
          <div className="absolute -top-8 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-70 text-white px-4 py-2 rounded text-sm whitespace-nowrap">
            バーコードをここに合わせてください
          </div>
        </div>

        {/* ステータス表示 */}
        {isScanning && (
          <div className="mt-8 bg-black bg-opacity-70 text-white px-6 py-3 rounded-lg">
            スキャン中...
          </div>
        )}
      </div>

      {/* 閉じるボタン */}
      <button
        onClick={handleClose}
        className="absolute top-4 right-4 bg-black bg-opacity-70 text-white px-4 py-2 rounded-lg pointer-events-auto hover:bg-opacity-90 transition-colors"
      >
        ✕ 閉じる
      </button>
    </div>
  );
}

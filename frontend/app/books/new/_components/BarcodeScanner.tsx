import { RefObject } from "react";
import styles from "../NewBookPage.module.css";
import { ScannerOverlay } from "./ScannerOverlay";
import { ErrorToast } from "./ErrorToast";

interface BarcodeScannerProps {
  videoRef: RefObject<HTMLVideoElement | null>;
  isScanning: boolean;
  isLookingUp: boolean;
  error?: string;
}

export function BarcodeScanner({
  videoRef,
  isScanning,
  isLookingUp,
  error,
}: BarcodeScannerProps) {
  return (
    <div className={styles["scanner-area"]}>
      {isLookingUp ? (
        <div className={styles["loading-overlay"]}>
          <p>書籍情報を取得中...</p>
        </div>
      ) : (
        <>
          <ErrorToast message={error} />
          <video ref={videoRef} className={styles.video} playsInline />
          <ScannerOverlay isScanning={isScanning} />
        </>
      )}
    </div>
  );
}

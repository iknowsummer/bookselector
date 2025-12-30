import styles from "../NewBookPage.module.css";

interface ScannerOverlayProps {
  isScanning: boolean;
}

export function ScannerOverlay({ isScanning }: ScannerOverlayProps) {
  return (
    <div className={styles.overlay}>
      <div className={styles["guide-text"]}>バーコードを中央に合わせて静止</div>
      {isScanning && <div className={styles.status}>スキャン中...</div>}
    </div>
  );
}

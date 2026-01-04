import styles from "../NewBookPage.module.css";

interface ErrorToastProps {
  message?: string;
}

export function ErrorToast({ message }: ErrorToastProps) {
  if (!message) return null;

  return <div className={styles["error-toast"]}>{message}</div>;
}

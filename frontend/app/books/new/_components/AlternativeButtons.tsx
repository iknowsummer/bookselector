import Link from "next/link";
import styles from "../NewBookPage.module.css";

export function AlternativeButtons() {
  return (
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
  );
}

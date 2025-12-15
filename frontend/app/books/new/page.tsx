"use client";

import Link from "next/link";
import styles from "./page.module.css";

export default function NewBookPage() {
  return (
    <div className="container">
      <h2>書籍登録</h2>

      <div className={styles["options-container"]}>
        <Link href="/books/new/scan">
          <button
            type="button"
            className={styles["option-button"]}
          >
            バーコードスキャンで登録
          </button>
        </Link>
        <Link href="/books/new/isbn">
          <button
            type="button"
            className={styles["option-button"]}
          >
            ISBNから登録
          </button>
        </Link>
        <Link href="/books/new/manual">
          <button
            type="button"
            className={styles["option-button"]}
          >
            手動で登録
          </button>
        </Link>
      </div>

      <div className={styles["back-button-container"]}>
        <Link href="/books">
          <button type="button">戻る</button>
        </Link>
      </div>
    </div>
  );
}

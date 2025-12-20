"use client";

import Link from "next/link";

export default function NewBookPage() {
  return (
    <div className="container">
      <h2>書籍登録</h2>

      <div className="options-container">
        <Link href="/books/new/scan">
          <button
            type="button"
            className="button option-button"
          >
            バーコードスキャンで登録
          </button>
        </Link>
        <Link href="/books/new/isbn">
          <button
            type="button"
            className="button option-button"
          >
            ISBNから登録
          </button>
        </Link>
        <Link href="/books/new/manual">
          <button
            type="button"
            className="button option-button"
          >
            手動で登録
          </button>
        </Link>
      </div>

      <div className="back-button-container">
        <Link href="/books">
          <button type="button" className="button">戻る</button>
        </Link>
      </div>
    </div>
  );
}

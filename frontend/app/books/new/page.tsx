"use client";

import Link from "next/link";

export default function NewBookPage() {
  return (
    <div className="container">
      <h2>書籍登録</h2>

      <div style={{
        display: "flex",
        flexDirection: "column",
        gap: "16px",
        maxWidth: "400px",
        margin: "32px auto"
      }}>
        <Link href="/books/new/scan">
          <button
            type="button"
            style={{
              width: "100%",
              padding: "16px",
              fontSize: "16px"
            }}
          >
            バーコードスキャンで登録
          </button>
        </Link>
        <Link href="/books/new/isbn">
          <button
            type="button"
            style={{
              width: "100%",
              padding: "16px",
              fontSize: "16px"
            }}
          >
            ISBNから登録
          </button>
        </Link>
        <Link href="/books/new/manual">
          <button
            type="button"
            style={{
              width: "100%",
              padding: "16px",
              fontSize: "16px"
            }}
          >
            手動で登録
          </button>
        </Link>
      </div>

      <div style={{ textAlign: "center", marginTop: "32px" }}>
        <Link href="/books">
          <button type="button">戻る</button>
        </Link>
      </div>
    </div>
  );
}

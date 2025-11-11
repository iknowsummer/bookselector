"use client";

import { useState, useCallback } from "react";
import { lookupBookByIsbn } from "@/lib/api/books";
import type { BookFormData } from "@/types/book";
import BarcodeScanner from "./BarcodeScanner";

type IsbnInputFormProps = {
  onSuccess: (bookData: BookFormData) => void;
  onManualEntry: (isbn?: string) => void;
  onCancel: () => void;
  autoFocus?: boolean;
};

export default function IsbnInputForm({
  onSuccess,
  onManualEntry,
  onCancel,
  autoFocus = true,
}: IsbnInputFormProps) {
  const [isbn, setIsbn] = useState<string>("");
  const [isLookingUp, setIsLookingUp] = useState(false);
  const [lookupError, setLookupError] = useState<string>("");
  const [showScanner, setShowScanner] = useState(false);

  const handleIsbnChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    // 空文字列 or 数字のみを許可
    if (value === "" || /^[0-9]+$/.test(value)) {
      setIsbn(value);
      if (lookupError) {
        setLookupError("");
      }
    }
  };

  const handleIsbnLookup = async () => {
    if (!isbn || isbn.length !== 13) {
      setLookupError("ISBNは13桁で入力してください");
      return;
    }

    setIsLookingUp(true);
    setLookupError("");

    try {
      const bookInfo = await lookupBookByIsbn(isbn);
      const bookData: BookFormData = {
        title: bookInfo.title,
        author: bookInfo.author,
        description: bookInfo.description,
        isbn: isbn,
        image_url: bookInfo.image_url,
        note: "",
      };
      onSuccess(bookData);
    } catch (err) {
      if (err instanceof Error) {
        setLookupError(err.message);
      } else {
        setLookupError("書籍情報の取得に失敗しました");
      }
    } finally {
      setIsLookingUp(false);
    }
  };

  const handleManualEntryClick = () => {
    onManualEntry(isbn || undefined);
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && isbn && isbn.length === 13) {
      handleIsbnLookup();
    }
  };

  const handleScanSuccess = useCallback((scannedIsbn: string) => {
    setShowScanner(false);
    setIsbn(scannedIsbn);
    setLookupError("");

    // スキャン成功後、自動的に情報取得
    setTimeout(async () => {
      try {
        setIsLookingUp(true);
        const bookInfo = await lookupBookByIsbn(scannedIsbn);
        const bookData: BookFormData = {
          title: bookInfo.title,
          author: bookInfo.author,
          description: bookInfo.description,
          isbn: scannedIsbn,
          image_url: bookInfo.image_url,
          note: "",
        };
        onSuccess(bookData);
      } catch (err) {
        if (err instanceof Error) {
          setLookupError(err.message);
        } else {
          setLookupError("書籍情報の取得に失敗しました");
        }
      } finally {
        setIsLookingUp(false);
      }
    }, 100);
  }, [onSuccess]);

  const handleScanError = useCallback((error: string) => {
    setShowScanner(false);
    setLookupError(error);
  }, []);

  const handleScannerClose = () => {
    setShowScanner(false);
  };

  return (
    <div className="isbn-input-form">
      {/* スキャナー表示中はフォームを非表示 */}
      {showScanner ? (
        <BarcodeScanner
          onScan={handleScanSuccess}
          onClose={handleScannerClose}
          onError={handleScanError}
        />
      ) : (
        <>
          <div className="form-group">
            <label>ISBN</label>
            <p style={{ fontSize: "14px", color: "#666", marginBottom: "8px" }}>
              ISBNを入力すると、書籍情報を自動取得できます
            </p>
            <div style={{ display: "flex", gap: "8px", marginBottom: "16px" }}>
              <input
                type="text"
                value={isbn}
                onChange={handleIsbnChange}
                onKeyPress={handleKeyPress}
                placeholder="9784XXXXXXXXX"
                maxLength={13}
                pattern="[0-9]*"
                style={{ flex: 1 }}
                autoFocus={autoFocus}
              />
              <button
                type="button"
                onClick={() => setShowScanner(true)}
                title="カメラでバーコードを読み取る"
              >
                📷
              </button>
              <button
                type="button"
                onClick={handleIsbnLookup}
                disabled={isLookingUp || !isbn || isbn.length !== 13}
              >
                {isLookingUp ? "取得中..." : "情報取得"}
              </button>
            </div>
            {lookupError && <div className="error-message">{lookupError}</div>}
          </div>

          <div style={{ textAlign: "center", margin: "24px 0" }}>
            <p style={{ fontSize: "14px", color: "#666", marginBottom: "12px" }}>
              または
            </p>
            <button type="button" onClick={handleManualEntryClick}>
              手動で登録
            </button>
          </div>

          <div style={{ marginTop: "24px" }}>
            <button type="button" onClick={onCancel}>
              キャンセル
            </button>
          </div>
        </>
      )}
    </div>
  );
}

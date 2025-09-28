"use client";
import { useCallback, useEffect, useState } from "react";

type Book = {
  id: number;
  title: string;
  author: string;
  description?: string | null;
  note?: string | null;
};

type Result = {
  id: number;
  book_ids: number[];
  note?: string | null;
  created_at: string;
};

export default function Home() {
  const apiBaseUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  const [apiStatus, setApiStatus] = useState<string>("");
  const [books, setBooks] = useState<Book[]>([]);
  const [message, setMessage] = useState<string>("");
  const [results, setResults] = useState<Result[]>([]);
  const [resultMessage, setResultMessage] = useState<string>("");

  const fetchResults = useCallback(async (): Promise<boolean> => {
    try {
      const res = await fetch(`${apiBaseUrl}/results/`);
      if (!res.ok) {
        throw new Error("リザルト一覧の取得に失敗しました");
      }
      const data: Result[] = await res.json();
      setResults(data);
      return true;
    } catch (error) {
      setResults([]);
      setResultMessage(`リザルト一覧の取得に失敗しました: ${error}`);
      return false;
    }
  }, [apiBaseUrl]);

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const res = await fetch(apiBaseUrl);
        if (!res.ok) {
          throw new Error("APIの取得に失敗しました");
        }
        const text = await res.text();
        setApiStatus(text);
      } catch (error) {
        setApiStatus(`APIステータスの取得に失敗しました: ${error}`);
      }
    };
    fetchStatus();
    fetchResults();
  }, [apiBaseUrl, fetchResults]);

  const fetchRandomBooks = async () => {
    setMessage("書籍情報を取得中です...");
    try {
      const res = await fetch(`${apiBaseUrl}/books/random/`);
      if (!res.ok) {
        throw new Error("書籍情報の取得に失敗しました");
      }
      const data: Book[] = await res.json();
      setBooks(data);
      if (data.length === 0) {
        setMessage("取得できる書籍情報がありませんでした");
      } else {
        setMessage("書籍情報を取得しました");
      }
    } catch (error) {
      setBooks([]);
      setMessage(`書籍情報の取得に失敗しました: ${error}`);
    }
  };

  const saveResult = async () => {
    if (books.length === 0) {
      setResultMessage("保存できる書籍情報がありません");
      return;
    }
    setResultMessage("リザルトを保存中です...");
    try {
      const res = await fetch(`${apiBaseUrl}/results/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          book_ids: books.map((book) => book.id),
        }),
      });
      if (!res.ok) {
        throw new Error("リザルトの保存に失敗しました");
      }
      await res.json();
      const succeeded = await fetchResults();
      if (succeeded) {
        setResultMessage("リザルトを保存しました");
      }
    } catch (error) {
      setResultMessage(`リザルトの保存に失敗しました: ${error}`);
    }
  };

  const deleteAllResults = async () => {
    if (results.length === 0) {
      setResultMessage("削除できるリザルトがありません");
      return;
    }
    setResultMessage("リザルトを削除中です...");
    try {
      const res = await fetch(`${apiBaseUrl}/results/`, {
        method: "DELETE",
      });
      if (!res.ok) {
        throw new Error("リザルトの削除に失敗しました");
      }
      await res.json();
      const succeeded = await fetchResults();
      if (succeeded) {
        setResultMessage("すべてのリザルトを削除しました");
      }
    } catch (error) {
      setResultMessage(`リザルトの削除に失敗しました: ${error}`);
    }
  };

  return (
    <main>
      <section>
        <h1>Book Selector</h1>
        <div>APIレスポンス: {apiStatus}</div>
      </section>
      <section>
        <button type="button" onClick={fetchRandomBooks}>
          ランダムに書籍情報を取得
        </button>
        <button type="button" onClick={saveResult} disabled={books.length === 0}>
          取得した書籍をリザルトとして保存
        </button>
        <button type="button" onClick={deleteAllResults} disabled={results.length === 0}>
          リザルトを全削除
        </button>
        <div>{message}</div>
        <ul>
          {books.map((book) => (
            <li key={book.id}>
              <div>タイトル: {book.title}</div>
              <div>著者: {book.author}</div>
              {book.description ? <div>説明: {book.description}</div> : null}
              {book.note ? <div>メモ: {book.note}</div> : null}
            </li>
          ))}
        </ul>
      </section>
      <section>
        <h2>保存済みリザルト</h2>
        <div>{resultMessage}</div>
        {results.length === 0 && resultMessage === "" ? (
          <div>保存されているリザルトはありません</div>
        ) : null}
        {results.length === 0 ? null : (
          <div>
            {results.map((result) => (
              <div
                key={result.id}
                style={{
                  border: "1px solid #ccc",
                  padding: "1rem",
                  marginBottom: "1rem",
                }}
              >
                <div>リザルトID: {result.id}</div>
                <div>
                  保存日時: {new Date(result.created_at).toLocaleString("ja-JP", {
                    year: "numeric",
                    month: "2-digit",
                    day: "2-digit",
                    hour: "2-digit",
                    minute: "2-digit",
                    second: "2-digit",
                  })}
                </div>
                {result.note ? <div>メモ: {result.note}</div> : null}
                <div>
                  書籍ID一覧:
                  <ul>
                    {result.book_ids.map((bookId) => (
                      <li key={bookId}>ID: {bookId}</li>
                    ))}
                  </ul>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    </main>
  );
}

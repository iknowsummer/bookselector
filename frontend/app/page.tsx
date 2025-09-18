"use client";
import { useEffect, useState } from "react";

export default function Home() {
  const [data, setData] = useState<string>("");

  useEffect(() => {
    const fetchData = async () => {
      try {
        const res = await fetch(
          process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
        );
        const text = await res.text();
        setData(text);
      } catch (err) {
        setData("API取得エラー");
      }
    };
    fetchData();
  }, []);

  return (
    <>
      <main>
        <h1>Welcome to Next.js!</h1>
        <div>APIレスポンス: {data}</div>
      </main>
      <footer>footer</footer>
    </>
  );
}

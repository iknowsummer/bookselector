import Link from "next/link";
import RandomBookList from "@/app/books/_components/RandomBookList";
import LatestBookList from "@/app/books/_components/LatestBookList";
import LoginPrompt from "@/app/components/LoginPrompt";
import { auth0 } from "@/lib/auth0";
import { fetchLatestBooks } from "@/lib/api/books";

export default async function Home() {
  const session = await auth0.getSession();

  if (!session) {
    return <LoginPrompt showDescription={true} title="ログインして始めましょう" />;
  }

  // 取得失敗時はフォールバックとして既存の2ブロック表示に倒す
  let hasBooks = true;
  try {
    const latest = await fetchLatestBooks(1);
    hasBooks = latest.length > 0;
  } catch (error) {
    console.error("Failed to fetch latest books:", error);
  }

  if (!hasBooks) {
    return (
      <section>
        <h2>まずは書籍登録をしましょう</h2>
        <p>
          書籍を登録すると、ランダムに1冊を取り出したり、最近の登録を一覧で見られるようになります。
        </p>
        <Link href="/books/new" className="button">
          書籍を登録する
        </Link>
      </section>
    );
  }

  return (
    <>
      <section>
        <h2>ランダム取得</h2>
      </section>
      <RandomBookList />
      <hr className="section-divider" />
      <section>
        <h2>最近の登録</h2>
        <LatestBookList limit={14} />
      </section>
    </>
  );
}

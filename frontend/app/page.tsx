import RandomBookList from "@/app/books/_components/RandomBookList";
import LatestBookList from "@/app/books/_components/LatestBookList";
import LoginPrompt from "@/app/components/LoginPrompt";
import { auth0 } from "@/lib/auth0";

export default async function Home() {
  const session = await auth0.getSession();

  if (!session) {
    return <LoginPrompt showDescription={true} title="ログインして始めましょう" />;
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

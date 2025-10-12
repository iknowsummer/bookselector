import RandomBookList from "@/components/RandomBookList";
import LatestBookList from "@/components/LatestBookList";

export default function Home() {
  return (
    <main>
      <section>
        <h2>最近の登録</h2>
        <LatestBookList limit={14} />
      </section>
      <section>
        <h2>ランダム取得</h2>
      </section>
      <RandomBookList />
    </main>
  );
}

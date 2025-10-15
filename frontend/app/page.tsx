import RandomBookList from "@/components/RandomBookList";
import LatestBookList from "@/components/LatestBookList";

export default function Home() {
  return (
    <>
      <section>
        <h2>ランダム取得</h2>
      </section>
      <RandomBookList />
      <hr style={{ border: "1px solid #eee", margin: "2rem 0" }} />
      <section>
        <h2>最近の登録</h2>
        <LatestBookList limit={14} />
      </section>
    </>
  );
}

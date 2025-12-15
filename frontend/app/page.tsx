import RandomBookList from "@/app/books/_components/RandomBookList";
import LatestBookList from "@/app/books/_components/LatestBookList";
import styles from "./page.module.css";

export default function Home() {
  return (
    <>
      <section>
        <h2>ランダム取得</h2>
      </section>
      <RandomBookList />
      <hr className={styles["section-divider"]} />
      <section>
        <h2>最近の登録</h2>
        <LatestBookList limit={14} />
      </section>
    </>
  );
}

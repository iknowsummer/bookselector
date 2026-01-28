import { redirect } from "next/navigation";
import { auth0 } from "@/lib/auth0";
import styles from "./dashboard.module.css";

export default async function Dashboard() {
  const session = await auth0.getSession();
  if (!session) {
    // 未ログインならリダイレクト
    redirect("/auth/login");
  }

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>ダッシュボード</h1>

      {/* ユーザー情報セクション */}
      <section className={styles.card}>
        <h2 className={styles.sectionTitle}>ユーザー情報</h2>
        <div className={styles.userInfo}>
          {session.user.picture && (
            <img
              src={session.user.picture}
              alt="プロフィール画像"
              className={styles.avatar}
            />
          )}
          <div className={styles.infoList}>
            <div className={styles.infoItem}>
              <span className={styles.label}>名前:</span>
              <span className={styles.value}>{session.user.name}</span>
            </div>
            <div className={styles.infoItem}>
              <span className={styles.label}>メールアドレス:</span>
              <span className={styles.value}>{session.user.email}</span>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
}

type LoginPromptProps = {
  title?: string;
  showDescription?: boolean;
};

export default function LoginPrompt({
  title = "ログインが必要です",
  showDescription = false,
}: LoginPromptProps) {
  return (
    <div className="login-prompt">
      {showDescription && (
        <div className="site-description">
          <h2>BookPitへようこそ</h2>
          <p>
            BookPitは、あなたの蔵書を管理し、次に読む本をランダムに選んでくれるWebアプリです。
          </p>
          <ul>
            <li>書籍の登録・管理（バーコードスキャン対応）</li>
            <li>本棚ごとに整理</li>
            <li>ランダム選書で次の一冊を決める</li>
          </ul>
        </div>
      )}
      <div className="login-message">
        <p>{title}</p>
        <a href="/auth/login" className="button">
          ログイン / アカウント作成
        </a>
      </div>
    </div>
  );
}

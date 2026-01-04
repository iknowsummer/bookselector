/**
 * Next.js Instrumentation Hook
 *
 * サーバー起動時にSSL証明書検証を設定する。
 *
 * 問題: 開発環境で自己署名SSL証明書（mkcert）を使用している。
 * Server ComponentがバックエンドAPIにfetchする際、Node.jsが証明書を拒否する。
 *
 * 解決策: 開発環境のみSSL証明書検証を無効化する。
 *
 * セキュリティ: NODE_ENV=developmentの場合のみ適用。
 * 本番環境では完全なSSL検証を維持する。
 */
export async function register() {
  if (process.env.NODE_ENV === 'development') {
    process.env.NODE_TLS_REJECT_UNAUTHORIZED = '0';

    console.log('[Instrumentation] Development mode: SSL certificate verification disabled');
    console.log('[Instrumentation] Backend API:', process.env.NEXT_PUBLIC_API_URL);
    console.log('[Instrumentation] WARNING: This should NEVER run in production!');
  } else {
    console.log('[Instrumentation] Production mode: SSL certificate verification enabled');
  }
}

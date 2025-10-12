import Link from "next/link";
import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <header>Book Selector</header>
        <main>
          <section id="nav">
            <ul>
              <li>
                <Link href="/">Home</Link>
              </li>
              <li>
                <Link href="/books/new">新規登録</Link>
              </li>
              <li>
                <Link href="/books">一覧</Link>
              </li>
            </ul>
          </section>

          {children}
        </main>
        <footer>footer</footer>
      </body>
    </html>
  );
}

import Link from "next/link";
import "./globals.css";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja">
      <body>
        <header>BookPit</header>
        <main>
          <nav id="global-nav">
            <ul>
              <li>
                <Link href="/">Home</Link>
              </li>
              <li>
                <Link href="/books/new">New Book</Link>
              </li>
              <li>
                <Link href="/books">Book List</Link>
              </li>
            </ul>
          </nav>

          {children}
        </main>
      </body>
    </html>
  );
}

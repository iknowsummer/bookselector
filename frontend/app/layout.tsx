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
          <section id="nav">
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
          </section>

          {children}
        </main>
      </body>
    </html>
  );
}

import Link from "next/link";
import "./globals.css";
import AuthMenu from "./components/AuthMenu";

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
              <li>
                <Link href="/shelves">Shelves</Link>
              </li>
              <li>
                <Link href="/dashboard">Dashboard</Link>
              </li>
              <li>
                <AuthMenu />
              </li>
            </ul>
          </nav>

          {children}
        </main>
      </body>
    </html>
  );
}

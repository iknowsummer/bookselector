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
        <main>{children}</main>
        <footer>footer</footer>
      </body>
    </html>
  );
}

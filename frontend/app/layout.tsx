import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "ETF Intelligence Lab",
  description: "Explore, compare and audit ETF datasets through explainable analytics.",
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

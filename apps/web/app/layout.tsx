import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "MatriBlood Q",
  description: "Voice-first quantum optimized obstetric emergency kit procurement"
};

export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}

import type { Metadata } from "next";
import { Plus_Jakarta_Sans } from "next/font/google";
import "./globals.css";

const plusJakarta = Plus_Jakarta_Sans({
  subsets: ["latin"],
  variable: "--font-plus-jakarta",
});

export const metadata: Metadata = {
  title: "HadesReality ContentOps",
  description: "AI-Assisted Social Media Publishing",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark h-full">
      <body
        className={`${plusJakarta.variable} font-sans antialiased bg-[#0a0f1d] text-white min-h-full flex flex-col`}
      >
        {children}
      </body>
    </html>
  );
}

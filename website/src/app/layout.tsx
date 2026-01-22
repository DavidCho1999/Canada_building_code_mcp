import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Canadian Building Code MCP - AI-Powered Code Search",
  description: "Search 14 Canadian building codes and 25,707 sections using natural language. AI-powered building code assistant for architects and engineers.",
  keywords: ["Canadian Building Code", "NBC", "OBC", "BCBC", "MCP", "AI", "building code search"],
  openGraph: {
    title: "Canadian Building Code MCP",
    description: "AI-powered search for Canadian building codes",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}

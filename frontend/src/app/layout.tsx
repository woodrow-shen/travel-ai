import type { Metadata } from "next";
import { Header } from "@/components/layout/Header";
import { Footer } from "@/components/layout/Footer";
import "./globals.css";

export const metadata: Metadata = {
  title: {
    default: "Travel AI - Smart Travel Planning",
    template: "%s | Travel AI",
  },
  description:
    "AI-powered travel planning with flight and hotel search, price comparison, and intelligent itinerary generation.",
  keywords: [
    "travel",
    "flights",
    "hotels",
    "AI",
    "itinerary",
    "price comparison",
  ],
  openGraph: {
    title: "Travel AI",
    description: "AI-powered travel planning and price comparison.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="flex min-h-screen flex-col antialiased">
        <Header />
        <main className="flex-1" id="main-content">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}

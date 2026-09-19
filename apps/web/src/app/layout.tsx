import type { Metadata } from "next";
import { Inter, JetBrains_Mono, Newsreader } from "next/font/google";
import "./globals.css";
import { Providers } from "@/components/Providers";

const inter = Inter({ 
  subsets: ["latin"],
  variable: "--font-inter",
});

const jetbrains = JetBrains_Mono({ 
  subsets: ["latin"],
  variable: "--font-jetbrains",
});

const newsreader = Newsreader({ 
  subsets: ["latin"],
  style: ['normal', 'italic'],
  variable: "--font-newsreader",
});

export const metadata: Metadata = {
  title: "Re:World | Narrative Instrument",
  description: "Multi-Agent Narrative Framework",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${inter.variable} ${jetbrains.variable} ${newsreader.variable} antialiased min-h-screen flex flex-col`}
      >
        <header className="border-b border-panel-border px-6 py-4 flex items-center justify-between shrink-0">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-canon shadow-[0_0_10px_rgba(234,179,8,0.5)]"></div>
            <h1 className="font-mono text-sm tracking-widest uppercase font-bold text-primary">Re:World</h1>
          </div>
          <div className="flex gap-4 font-mono text-xs text-primary-muted uppercase tracking-wider">
            <span>Status: Online</span>
            <span>Canon: Secure</span>
          </div>
        </header>
        <main className="flex-1 flex flex-col overflow-hidden">
          <Providers>
            {children}
          </Providers>
        </main>
      </body>
    </html>
  );
}

import type { Metadata } from "next";
import { AppProviders } from "../lib/providers";
import { themeInitScript } from "../lib/theme";
import "./globals.css";

export const metadata: Metadata = {
  title: "IP-SAKTI Navigator | Ayurvedic IP & Regulatory Roadmaps",
  description:
    "Turn an Ayurvedic innovation into an evidence-backed IP and regulatory roadmap. Evidence-first decision support scoped to Indian statutes.",
  icons: {
    icon: "/favicon.jpeg",
    apple: "/favicon.jpeg",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html
      lang="en"
      suppressHydrationWarning
      className="h-full antialiased"
    >
      <body className="min-h-full flex flex-col">
        <script dangerouslySetInnerHTML={{ __html: themeInitScript }} />
        <AppProviders>{children}</AppProviders>
      </body>
    </html>
  );
}

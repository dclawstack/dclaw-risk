import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AppShell } from "@/components/app-shell";
import { RiskCopilot } from "@/components/risk-copilot";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "DClaw Risk",
  description: "Enterprise risk management with AI insights",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AppShell>{children}</AppShell>
        <RiskCopilot />
      </body>
    </html>
  );
}

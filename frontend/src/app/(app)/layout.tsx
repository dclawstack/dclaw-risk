import { AppShell } from "@/components/app-shell";
import { RiskCopilot } from "@/components/risk-copilot";

export default function AppLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <>
      <AppShell>{children}</AppShell>
      <RiskCopilot />
    </>
  );
}

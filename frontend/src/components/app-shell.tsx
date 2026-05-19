"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { ShieldAlert, ListChecks, Activity, ShieldCheck } from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Dashboard", icon: Activity },
  { href: "/risks", label: "Risk register", icon: ListChecks },
  { href: "/controls", label: "Controls", icon: ShieldCheck },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  return (
    <div className="min-h-screen flex bg-slate-50">
      <aside className="w-60 bg-white border-r border-slate-200 flex flex-col">
        <div className="flex items-center gap-3 px-5 py-5 border-b border-slate-200">
          <ShieldAlert className="w-7 h-7" style={{ color: "#10B981" }} />
          <div>
            <div className="font-semibold leading-tight">DClaw Risk</div>
            <div className="text-xs text-slate-500">Governance</div>
          </div>
        </div>
        <nav className="flex-1 px-3 py-4 space-y-1">
          {NAV.map(({ href, label, icon: Icon }) => {
            const active =
              href === "/" ? pathname === "/" : pathname.startsWith(href);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-3 rounded-md px-3 py-2 text-sm transition-colors",
                  active
                    ? "bg-emerald-50 text-emerald-700 font-medium"
                    : "text-slate-600 hover:bg-slate-100"
                )}
              >
                <Icon className="w-4 h-4" />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="px-5 py-4 border-t border-slate-200 text-xs text-slate-400">
          v1.0 · P0 demo
        </div>
      </aside>
      <main className="flex-1 min-w-0 p-6">{children}</main>
    </div>
  );
}

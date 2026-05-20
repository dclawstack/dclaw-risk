import Link from "next/link";
import { ArrowRight, ListChecks, ShieldCheck, Activity } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

const TILES = [
  {
    href: "/risks",
    title: "Risk Register",
    description: "Identify, score, and track risks with AI-assisted classification.",
    icon: ListChecks,
  },
  {
    href: "/controls",
    title: "Controls",
    description: "Catalogue controls and map them to risks with effectiveness scores.",
    icon: ShieldCheck,
  },
];

export default function Dashboard() {
  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <header className="space-y-1">
        <div className="flex items-center gap-2 text-emerald-700">
          <Activity className="w-5 h-5" />
          <h1 className="text-2xl font-semibold">DClaw Risk</h1>
        </div>
        <p className="text-slate-600 max-w-2xl">
          Enterprise risk management with AI insights. Identify risks, run
          qualitative or quantitative (FAIR Monte Carlo) assessments, and map
          mitigating controls. Talk to the Copilot in the bottom-right at any
          time.
        </p>
      </header>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {TILES.map(({ href, title, description, icon: Icon }) => (
          <Link key={href} href={href} className="group">
            <Card className="hover:border-emerald-400 transition-colors h-full">
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-base font-semibold">{title}</CardTitle>
                <Icon className="w-5 h-5 text-emerald-600" />
              </CardHeader>
              <CardContent>
                <CardDescription>{description}</CardDescription>
                <div className="mt-3 flex items-center gap-1 text-sm text-emerald-700">
                  Open <ArrowRight className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
                </div>
              </CardContent>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  );
}

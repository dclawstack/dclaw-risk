import Link from "next/link";
import {
  ShieldAlert,
  ArrowRight,
  Github,
  Bot,
  ListChecks,
  Sigma,
  ShieldCheck,
  BarChart3,
  Gauge,
  AlertTriangle,
  Layers,
  Building2,
  Radio,
  Users,
  ScrollText,
  BookOpen,
  Sparkles,
  Database,
  Zap,
} from "lucide-react";
import { DemoSection } from "@/components/demo-section";

const FEATURES = [
  {
    icon: Bot,
    title: "AI Risk Copilot",
    badge: "P0.1",
    description:
      "A domain-aware chat assistant that knows every risk in your register. Ask it to identify new risks from a project brief, classify a draft risk into severity / probability, or explain why an exposure number changed.",
    bullets: [
      "Ollama (local) → OpenRouter (cloud) fallback chain",
      "TF-IDF retrieval over your knowledge base feeds every reply",
      "Suggested actions extracted from each response",
    ],
  },
  {
    icon: ListChecks,
    title: "Risk Register",
    badge: "P0.2",
    description:
      "Full CRUD register with category filtering, status workflow (identified → assessed → treated → monitored → closed), and a 5×5 heat map that updates as severity and probability change.",
    bullets: [
      "AI-assisted category + severity classification",
      "Per-risk time-series trend from assessment history",
      "Owner, velocity, and AI rationale captured per row",
    ],
  },
  {
    icon: Sigma,
    title: "FAIR Monte Carlo Assessment",
    badge: "P0.3",
    description:
      "Triangular-distribution loss magnitude × uniform-distribution event frequency, simulated thousands of times. Persists P10/P50/P90/mean and a 50-point loss-exceedance curve.",
    bullets: [
      "Deterministic with a seed, suitable for unit testing",
      "Qualitative scoring also supported, auto-syncs onto the parent risk",
      "Loss-exceedance curve rendered as inline SVG",
    ],
  },
  {
    icon: ShieldCheck,
    title: "Control Mapping",
    badge: "P0.4",
    description:
      "Catalogue controls (preventive / detective / corrective / compensating), map them to risks with per-link effectiveness scoring, and run gap analysis to see uncovered risks and unused controls.",
    bullets: [
      "Many-to-many association with per-link effectiveness 1-5",
      "Framework tagging (NIST 800-53, ISO 27001, SOC 2)",
      "Two-sided gap analysis endpoint",
    ],
  },
  {
    icon: BarChart3,
    title: "Risk Reporting",
    badge: "P1.3",
    description:
      "Executive-ready aggregates: counts by category and status, top-N risks, mean qualitative score, control coverage %, and total annualised P50/P90 exposure across all quantified risks.",
    bullets: [
      "AI-written 3-paragraph board narrative, grounded only in real numbers",
      "Per-risk exposure roll-up using the latest quantitative assessment",
      "Compares qualitative posture to quantitative loss exposure",
    ],
  },
  {
    icon: Gauge,
    title: "Key Risk Indicators",
    badge: "P1.2",
    description:
      "Track operational metrics that signal risk crossing tolerance. Warn / critical thresholds with above-or-below direction, auto-derived status, and a breaches feed for the dashboard.",
    bullets: [
      "Optional FK to a Risk so breaches surface contextually",
      "Direction switch handles both 'higher is worse' and 'lower is worse'",
      "Per-KRI custom units and owner",
    ],
  },
  {
    icon: AlertTriangle,
    title: "Incident Linkage",
    badge: "P1.1",
    description:
      "Log realised incidents and link them to risks in the register. The Copilot mines the incident log for recurring themes and surfaces them by risk category.",
    bullets: [
      "AI pattern detection across the last 50 incidents",
      "Severity 1-5 + status workflow",
      "Patterns categorised by risk family (operational, cyber, supplier...)",
    ],
  },
  {
    icon: Layers,
    title: "Scenario Planning",
    badge: "P2.4",
    description:
      "Define what-if multipliers per risk category, then stress-test the entire register in one click. Returns baseline vs. projected scores with a delta % so you can see where exposure concentrates.",
    bullets: [
      "AI scenario generation from a free-text description",
      "Per-risk projected severity, probability, score",
      "Stored as JSONB so multipliers are auditable and versionable",
    ],
  },
  {
    icon: Building2,
    title: "Third-Party Risk",
    badge: "P2.3",
    description:
      "Vendor catalogue with criticality 1-5 and a 0-100 risk score. Click 'AI score' to get an LLM-generated score plus a rationale tied to the vendor's category and any notes.",
    bullets: [
      "Last-assessed-at tracked per vendor",
      "Rationale preserved alongside the score",
      "Heuristic fallback when the LLM is unreachable",
    ],
  },
  {
    icon: Radio,
    title: "Emerging Risk Feed",
    badge: "P2.1",
    description:
      "Pluggable feed reader with the NIST NVD CVE 2.0 JSON API wired in by default (CVSS → 1-5 impact mapping). Add a new feed by registering a single async function.",
    bullets: [
      "Cross-feed deduplication on (source, title)",
      "Synthetic feed for offline / CI environments",
      "CVE detail links rendered in the UI",
    ],
  },
  {
    icon: Users,
    title: "Risk Culture Surveys",
    badge: "P2.2",
    description:
      "Author surveys with one or more dimensions (Speak-up, Tone-at-top, Accountability). Anonymous respondents submit 0-100 scores. Closing a survey auto-aggregates responses into per-dimension culture scores.",
    bullets: [
      "Opaque respondent hash — no PII stored",
      "Multi-question, multi-dimension support",
      "Aggregated scores feed the reporting dashboard",
    ],
  },
  {
    icon: ScrollText,
    title: "Compliance Coverage",
    badge: "P1.4",
    description:
      "Joined view of compliance requirements (ISO 27001:2022, SOC 2 Type II, NIST 800-53 Rev 5) against your local control library. Coverage % per framework, plus a per-requirement gap list.",
    bullets: [
      "Configurable to proxy to a real DClaw Compliance instance",
      "Mock-mode fixture so the demo always renders",
      "Push your control library upstream with one API call",
    ],
  },
  {
    icon: BookOpen,
    title: "Knowledge Base + RAG",
    badge: "Copilot",
    description:
      "Upload policies, runbooks, and procedures. The Copilot retrieves the top-3 most relevant passages for every user query using TF-IDF cosine similarity and grounds its answer in your text.",
    bullets: [
      "Dependency-free retriever — no vector DB required",
      "Search endpoint to preview retrieval before it hits the Copilot",
      "Swap in a Qdrant-backed retriever without touching call sites",
    ],
  },
];

const STACK = [
  { label: "Frontend", value: "Next.js 14 App Router · Tailwind · shadcn/ui" },
  { label: "Backend", value: "FastAPI · Pydantic v2 · SQLAlchemy 2.0 async" },
  { label: "Database", value: "PostgreSQL 16 · Alembic migrations" },
  { label: "LLM", value: "Ollama (local) → OpenRouter (cloud) fallback" },
  { label: "Auth", value: "Logto JWT (with DEV bypass for development)" },
  { label: "Numerics", value: "NumPy for FAIR Monte Carlo simulation" },
];

const REPO_URL = "https://github.com/dclawstack/dclaw-risk";

export default function LandingPage() {
  return (
    <main className="bg-white text-slate-900">
      <NavBar />
      <Hero />
      <StatsBar />
      <DemoSection />
      <FeatureGrid />
      <CopilotSpotlight />
      <FairSpotlight />
      <StackSection />
      <CtaSection />
      <Footer />
    </main>
  );
}

function NavBar() {
  return (
    <header className="border-b border-slate-100">
      <div className="mx-auto max-w-6xl px-6 h-16 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-6 h-6" style={{ color: "#10B981" }} />
          <span className="font-semibold">DClaw Risk</span>
          <span className="text-xs text-slate-400 ml-2">Governance · v1.0</span>
        </div>
        <nav className="flex items-center gap-5 text-sm">
          <a href="#demo" className="text-slate-600 hover:text-slate-900">
            Demo
          </a>
          <a href="#features" className="text-slate-600 hover:text-slate-900">
            Features
          </a>
          <a href="#copilot" className="text-slate-600 hover:text-slate-900">
            Copilot
          </a>
          <a href="#stack" className="text-slate-600 hover:text-slate-900">
            Stack
          </a>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="text-slate-600 hover:text-slate-900 inline-flex items-center gap-1"
          >
            <Github className="w-4 h-4" />
            GitHub
          </a>
          <Link
            href="/dashboard"
            className="rounded-md bg-emerald-600 px-3 py-1.5 text-white text-sm font-medium hover:bg-emerald-700"
          >
            Open app
          </Link>
        </nav>
      </div>
    </header>
  );
}

function Hero() {
  return (
    <section className="relative overflow-hidden">
      <div
        className="absolute inset-0 -z-10 opacity-50"
        style={{
          background:
            "radial-gradient(60% 50% at 50% 0%, rgba(16,185,129,0.15), transparent 70%)",
        }}
      />
      <div className="mx-auto max-w-6xl px-6 pt-20 pb-24 text-center">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 text-emerald-700 px-3 py-1 text-xs font-medium">
          <Sparkles className="w-3.5 h-3.5" />
          AI-native enterprise risk management
        </span>
        <h1 className="mt-6 text-5xl md:text-6xl font-bold tracking-tight">
          Enterprise risk you can
          <br />
          <span className="text-emerald-600">actually quantify.</span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-600">
          Identify risks with a domain-aware Copilot. Score them qualitatively
          or run a FAIR Monte Carlo simulation. Map controls, track KRIs, model
          scenarios. All in one open-source stack.
        </p>
        <div className="mt-8 flex items-center justify-center gap-3">
          <Link
            href="/dashboard"
            className="inline-flex items-center gap-2 rounded-md bg-emerald-600 px-5 py-3 text-white font-medium hover:bg-emerald-700"
          >
            Open the app
            <ArrowRight className="w-4 h-4" />
          </Link>
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-5 py-3 font-medium text-slate-900 hover:bg-slate-50"
          >
            <Github className="w-4 h-4" />
            View on GitHub
          </a>
        </div>
        <p className="mt-6 text-xs text-slate-500">
          70 API endpoints · 13 pages · 28 tests passing · MIT licence
        </p>
      </div>
    </section>
  );
}

function StatsBar() {
  const stats = [
    { label: "PRD features", value: "12 / 12" },
    { label: "API endpoints", value: "70" },
    { label: "Tests passing", value: "28 / 28" },
    { label: "FAIR iterations", value: "10k+" },
  ];
  return (
    <section className="border-y border-slate-100 bg-slate-50">
      <div className="mx-auto max-w-6xl px-6 py-10 grid grid-cols-2 md:grid-cols-4 gap-6">
        {stats.map((s) => (
          <div key={s.label} className="text-center">
            <div className="text-3xl font-bold text-slate-900 tabular-nums">
              {s.value}
            </div>
            <div className="text-xs text-slate-500 mt-1">{s.label}</div>
          </div>
        ))}
      </div>
    </section>
  );
}

function FeatureGrid() {
  return (
    <section id="features" className="mx-auto max-w-6xl px-6 py-24">
      <div className="text-center max-w-2xl mx-auto">
        <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
          Everything the PRD asks for.
        </h2>
        <p className="mt-4 text-slate-600">
          13 features across P0 foundation, P1 platform, and P2 vertical
          layers. Each one ships with an AI angle, a working backend, and a
          frontend page.
        </p>
      </div>

      <div className="mt-14 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
        {FEATURES.map(({ icon: Icon, title, badge, description, bullets }) => (
          <article
            key={title}
            className="rounded-xl border border-slate-200 bg-white p-6 hover:border-emerald-300 hover:shadow-sm transition-all"
          >
            <div className="flex items-center justify-between">
              <div className="rounded-md bg-emerald-50 p-2 text-emerald-700">
                <Icon className="w-5 h-5" />
              </div>
              <span className="rounded-full bg-slate-100 px-2 py-0.5 text-xs font-medium text-slate-600">
                {badge}
              </span>
            </div>
            <h3 className="mt-4 font-semibold text-lg">{title}</h3>
            <p className="mt-2 text-sm text-slate-600">{description}</p>
            <ul className="mt-3 space-y-1 text-xs text-slate-500">
              {bullets.map((b) => (
                <li key={b} className="flex gap-2">
                  <span className="text-emerald-500">·</span>
                  {b}
                </li>
              ))}
            </ul>
          </article>
        ))}
      </div>
    </section>
  );
}

function CopilotSpotlight() {
  return (
    <section
      id="copilot"
      className="bg-slate-900 text-slate-100"
    >
      <div className="mx-auto max-w-6xl px-6 py-24 grid md:grid-cols-2 gap-12 items-center">
        <div>
          <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/15 text-emerald-300 px-3 py-1 text-xs font-medium">
            <Bot className="w-3.5 h-3.5" />
            Copilot mandate · §9
          </span>
          <h2 className="mt-5 text-3xl md:text-4xl font-bold tracking-tight">
            Every page has a Copilot that knows your data.
          </h2>
          <p className="mt-5 text-slate-300">
            The floating chat in the bottom-right knows every risk, every
            control, and every document you've uploaded. It retrieves the
            three most relevant knowledge-base passages for each question
            using TF-IDF and grounds the LLM response in your text — so
            answers are specific, not generic.
          </p>
          <ul className="mt-6 space-y-2 text-sm text-slate-300">
            {[
              "Risk register injected into the system prompt",
              "TF-IDF retrieval over your knowledge base on every query",
              "Suggested actions extracted from every reply",
              "Falls back: Ollama (local) → OpenRouter (cloud) → mock",
            ].map((line) => (
              <li key={line} className="flex gap-2">
                <Zap className="w-4 h-4 mt-0.5 shrink-0 text-emerald-400" />
                {line}
              </li>
            ))}
          </ul>
        </div>
        <div className="rounded-xl border border-slate-700/60 bg-slate-800/70 p-5 shadow-xl">
          <div className="text-xs text-slate-400 mb-3">Copilot transcript</div>
          <div className="space-y-3 text-sm">
            <div className="bg-emerald-600 text-white rounded-lg px-3 py-2 max-w-[85%] ml-auto">
              What's our top risk and what should I do?
            </div>
            <div className="bg-slate-700/60 rounded-lg px-3 py-2 max-w-[85%]">
              Your top risk is{" "}
              <strong>Cloud provider outage</strong> [Operational], severity 5 ×
              probability 4. Three actions:
              <ul className="mt-2 list-disc pl-5 space-y-1">
                <li>Schedule a workshop with the SRE team this week</li>
                <li>Invest 20 % of cloud spend in a secondary region</li>
                <li>Mirror critical apps between providers for faster recovery</li>
              </ul>
            </div>
            <div className="text-xs text-slate-500">via ollama+openrouter+mock</div>
          </div>
        </div>
      </div>
    </section>
  );
}

function FairSpotlight() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-24 grid md:grid-cols-2 gap-12 items-center">
      <div className="order-2 md:order-1">
        <div className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm">
          <div className="text-xs text-slate-500 mb-2">
            FAIR Monte Carlo — 10,000 iterations
          </div>
          <div className="grid grid-cols-4 gap-3 mb-4">
            <Stat label="P10" value="$88k" />
            <Stat label="P50" value="$320k" />
            <Stat label="P90" value="$911k" />
            <Stat label="Mean" value="$419k" highlight />
          </div>
          <svg viewBox="0 0 400 120" className="w-full">
            <rect x="0" y="0" width="400" height="120" fill="#f8fafc" />
            <path
              d="M 10 10 Q 60 20 100 35 T 220 80 T 390 110"
              fill="none"
              stroke="#10B981"
              strokeWidth="2.5"
            />
            <text x="10" y="115" fontSize="9" fill="#64748b">
              $9k
            </text>
            <text x="385" y="115" fontSize="9" fill="#64748b" textAnchor="end">
              $1.7M
            </text>
          </svg>
          <div className="text-[10px] text-slate-400 mt-1">
            Annualised loss-exceedance curve
          </div>
        </div>
      </div>
      <div className="order-1 md:order-2">
        <span className="inline-flex items-center gap-1.5 rounded-full bg-emerald-50 text-emerald-700 px-3 py-1 text-xs font-medium">
          <Sigma className="w-3.5 h-3.5" />
          P0.3 · Risk Assessment
        </span>
        <h2 className="mt-5 text-3xl md:text-4xl font-bold tracking-tight">
          Quantify exposure with FAIR Monte Carlo.
        </h2>
        <p className="mt-5 text-slate-600">
          Give us your loss range (min / mode / max) and event frequency band.
          We sample a triangular loss distribution and a uniform frequency
          thousands of times, then return percentiles and a full
          loss-exceedance curve. Deterministic with a seed, so the math is unit
          testable.
        </p>
        <div className="mt-6 grid grid-cols-2 gap-3">
          {[
            { l: "Loss model", v: "Triangular(min, mode, max)" },
            { l: "Frequency model", v: "Uniform(min, max) per year" },
            { l: "Default iterations", v: "10,000" },
            { l: "Output", v: "P10/P50/P90/mean + 50-point curve" },
          ].map((kv) => (
            <div
              key={kv.l}
              className="rounded-md border border-slate-200 bg-white p-3"
            >
              <div className="text-xs text-slate-500">{kv.l}</div>
              <div className="text-sm font-medium">{kv.v}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function Stat({
  label,
  value,
  highlight,
}: {
  label: string;
  value: string;
  highlight?: boolean;
}) {
  return (
    <div
      className={
        "rounded-md p-2 " +
        (highlight ? "bg-emerald-50 border border-emerald-200" : "bg-slate-50")
      }
    >
      <div className="text-[10px] text-slate-500">{label}</div>
      <div className="font-semibold tabular-nums">{value}</div>
    </div>
  );
}

function StackSection() {
  return (
    <section id="stack" className="bg-slate-50 border-y border-slate-100">
      <div className="mx-auto max-w-6xl px-6 py-20">
        <div className="text-center max-w-2xl mx-auto">
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
            Boring, proven stack.
          </h2>
          <p className="mt-4 text-slate-600">
            No JavaScript-of-the-week. Everything in production use at scale,
            chosen so anyone on your team can read and extend it.
          </p>
        </div>
        <div className="mt-12 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {STACK.map((s) => (
            <div
              key={s.label}
              className="rounded-lg border border-slate-200 bg-white p-5"
            >
              <div className="flex items-center gap-2 text-emerald-700">
                <Database className="w-4 h-4" />
                <div className="text-xs font-semibold uppercase tracking-wide">
                  {s.label}
                </div>
              </div>
              <div className="mt-2 font-medium text-slate-900">{s.value}</div>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function CtaSection() {
  return (
    <section className="mx-auto max-w-6xl px-6 py-24 text-center">
      <h2 className="text-3xl md:text-4xl font-bold tracking-tight">
        Run it locally in two commands.
      </h2>
      <p className="mt-4 max-w-2xl mx-auto text-slate-600">
        Clone the repo, copy <code className="bg-slate-100 px-1.5 py-0.5 rounded text-sm">.env.example</code> to{" "}
        <code className="bg-slate-100 px-1.5 py-0.5 rounded text-sm">.env</code>, then{" "}
        <code className="bg-slate-100 px-1.5 py-0.5 rounded text-sm">docker compose up --build</code>.
      </p>
      <div className="mt-8 flex items-center justify-center gap-3">
        <a
          href={REPO_URL}
          target="_blank"
          rel="noreferrer"
          className="inline-flex items-center gap-2 rounded-md bg-slate-900 px-5 py-3 text-white font-medium hover:bg-slate-800"
        >
          <Github className="w-4 h-4" />
          dclawstack/dclaw-risk
        </a>
        <Link
          href="/dashboard"
          className="inline-flex items-center gap-2 rounded-md border border-slate-300 bg-white px-5 py-3 font-medium text-slate-900 hover:bg-slate-50"
        >
          Try the app
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </section>
  );
}

function Footer() {
  return (
    <footer className="border-t border-slate-100">
      <div className="mx-auto max-w-6xl px-6 py-10 flex flex-col md:flex-row items-center justify-between gap-3 text-sm text-slate-500">
        <div className="flex items-center gap-2">
          <ShieldAlert className="w-4 h-4" style={{ color: "#10B981" }} />
          <span>DClaw Risk</span>
          <span className="text-slate-300">·</span>
          <span>Governance category · port 3068 / 8155</span>
        </div>
        <div className="flex items-center gap-4">
          <a
            href={REPO_URL}
            target="_blank"
            rel="noreferrer"
            className="hover:text-slate-900 inline-flex items-center gap-1"
          >
            <Github className="w-4 h-4" />
            Source
          </a>
          <Link href="/dashboard" className="hover:text-slate-900">
            Open app
          </Link>
        </div>
      </div>
    </footer>
  );
}

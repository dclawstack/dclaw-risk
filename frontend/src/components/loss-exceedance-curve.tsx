"use client";

import type { CurvePoint } from "@/lib/api";

const WIDTH = 600;
const HEIGHT = 220;
const PAD = { left: 56, right: 12, top: 12, bottom: 28 };

export function LossExceedanceCurve({ points }: { points: CurvePoint[] }) {
  if (!points || points.length === 0) {
    return (
      <div className="text-sm text-slate-500">No curve data yet.</div>
    );
  }
  const maxLoss = Math.max(...points.map((p) => p.loss));
  const minLoss = Math.min(...points.map((p) => p.loss));
  const xSpan = Math.max(1, maxLoss - minLoss);
  const plotW = WIDTH - PAD.left - PAD.right;
  const plotH = HEIGHT - PAD.top - PAD.bottom;

  function x(loss: number): number {
    return PAD.left + ((loss - minLoss) / xSpan) * plotW;
  }
  function y(prob: number): number {
    return PAD.top + (1 - prob) * plotH;
  }

  const path = points
    .map((p, i) => `${i === 0 ? "M" : "L"}${x(p.loss).toFixed(1)},${y(p.exceedance_probability).toFixed(1)}`)
    .join(" ");

  const yTicks = [0, 0.25, 0.5, 0.75, 1];
  const xTickValues = [
    minLoss,
    minLoss + xSpan * 0.25,
    minLoss + xSpan * 0.5,
    minLoss + xSpan * 0.75,
    maxLoss,
  ];

  return (
    <div className="w-full overflow-x-auto">
      <svg
        viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
        className="w-full h-auto text-xs"
        role="img"
        aria-label="Loss exceedance curve"
      >
        <rect
          x={PAD.left}
          y={PAD.top}
          width={plotW}
          height={plotH}
          fill="#f8fafc"
          stroke="#e2e8f0"
        />
        {yTicks.map((t) => (
          <g key={t}>
            <line
              x1={PAD.left}
              x2={PAD.left + plotW}
              y1={y(t)}
              y2={y(t)}
              stroke="#e2e8f0"
              strokeDasharray="2 2"
            />
            <text
              x={PAD.left - 6}
              y={y(t) + 3}
              textAnchor="end"
              fill="#64748b"
            >
              {Math.round(t * 100)}%
            </text>
          </g>
        ))}
        {xTickValues.map((t, i) => (
          <text
            key={i}
            x={x(t)}
            y={HEIGHT - 8}
            textAnchor="middle"
            fill="#64748b"
          >
            ${formatCompact(t)}
          </text>
        ))}
        <path d={path} fill="none" stroke="#10B981" strokeWidth={2} />
        <text
          x={PAD.left}
          y={PAD.top - 2}
          fill="#64748b"
          fontSize={10}
        >
          P(annual loss ≥ x)
        </text>
      </svg>
    </div>
  );
}

function formatCompact(n: number): string {
  if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(1)}M`;
  if (n >= 1_000) return `${(n / 1_000).toFixed(0)}k`;
  return `${Math.round(n)}`;
}

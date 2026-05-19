"use client";

import type { Risk } from "@/lib/api";
import { cn } from "@/lib/utils";

const ROWS = 5;
const COLS = 5;

function cellColor(severity: number, probability: number): string {
  const score = severity * probability;
  if (score >= 16) return "bg-red-500/80";
  if (score >= 9) return "bg-amber-400/80";
  if (score >= 4) return "bg-emerald-400/80";
  return "bg-emerald-200/80";
}

export function HeatMap({ risks }: { risks: Risk[] }) {
  const grid: Risk[][][] = Array.from({ length: ROWS }, () =>
    Array.from({ length: COLS }, () => [])
  );
  for (const r of risks) {
    const sev = Math.min(5, Math.max(1, r.severity)) - 1;
    const prob = Math.min(5, Math.max(1, r.probability)) - 1;
    // Row 0 = severity 5 (top); Col 0 = probability 1 (left)
    grid[ROWS - 1 - sev][prob].push(r);
  }
  return (
    <div className="space-y-2">
      <div className="flex items-center gap-2">
        <div className="w-8 text-xs text-slate-400 -rotate-90 origin-center">
          Severity
        </div>
        <div className="flex-1 grid grid-cols-5 gap-1">
          {grid.flatMap((row, rIdx) =>
            row.map((cell, cIdx) => (
              <div
                key={`${rIdx}-${cIdx}`}
                className={cn(
                  "aspect-square rounded-md flex items-center justify-center text-white font-semibold text-sm relative",
                  cellColor(ROWS - rIdx, cIdx + 1)
                )}
                title={`Severity ${ROWS - rIdx}, Probability ${cIdx + 1}`}
              >
                {cell.length > 0 && cell.length}
              </div>
            ))
          )}
        </div>
      </div>
      <div className="flex items-center justify-between text-xs text-slate-400 pl-8">
        <span>Probability →</span>
        <span>1 · 2 · 3 · 4 · 5</span>
      </div>
    </div>
  );
}

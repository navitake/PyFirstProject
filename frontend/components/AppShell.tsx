"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { createContext, useCallback, useContext, useEffect, useRef, useState } from "react";
import { api, type CompleteResult, type Stats } from "@/lib/api";
import { CATEGORIES, LABEL, type Stat } from "@/lib/categories";

type Toast = { id: number; text: string; stat?: Stat; tone: "gain" | "info" | "error" };

type ShellContext = {
  stats: Stats | null;
  setStats: (s: Stats) => void;
  notify: (text: string, tone?: Toast["tone"], stat?: Stat) => void;
  showGain: (r: CompleteResult) => void;
};

const Ctx = createContext<ShellContext | null>(null);

export function useShell() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useShell は AppShell の中で使う");
  return ctx;
}

const NAV = [
  { href: "/", label: "今日" },
  { href: "/tasks", label: "すべて" },
  { href: "/habits", label: "繰り返し" },
];

export default function AppShell({ children }: { children: React.ReactNode }) {
  const [stats, setStats] = useState<Stats | null>(null);
  const [toast, setToast] = useState<Toast | null>(null);
  const [pulse, setPulse] = useState<Stat | null>(null);
  const seq = useRef(0);
  const pathname = usePathname();

  const notify = useCallback((text: string, tone: Toast["tone"] = "info", stat?: Stat) => {
    const id = ++seq.current;
    setToast({ id, text, tone, stat });
    setTimeout(() => setToast((t) => (t?.id === id ? null : t)), 2600);
  }, []);

  const showGain = useCallback(
    (r: CompleteResult) => {
      setStats(r.stats);
      if (!r.gain) return notify("完了しました（分解元のタスクは加算されません）");
      const { stat, amount, capped } = r.gain;
      if (capped) return notify(`今日の${LABEL[stat]}は3件に達しているので、加算はありません`, "info", stat);
      setPulse(stat);
      setTimeout(() => setPulse(null), 900);
      notify(`${stat} +${amount}`, "gain", stat);
    },
    [notify],
  );

  useEffect(() => {
    api.stats().then(setStats).catch((e) => notify(e.message, "error"));
  }, [notify]);

  return (
    <Ctx.Provider value={{ stats, setStats, notify, showGain }}>
      <header className="statbar" aria-label="今週のステータス">
        <div className="statbar-inner">
          {CATEGORIES.map(({ stat, label }) => {
            const value = stats?.stats[stat] ?? 0;
            const left = stats?.remaining_today[stat] ?? 3;
            return (
              <div key={stat} className={`stat ${pulse === stat ? "pulse" : ""}`} data-stat={stat}>
                <div className="stat-head">
                  <span className="stat-key">{stat}</span>
                  <span className="stat-val num">{value}</span>
                </div>
                <div className="stat-meter" aria-hidden>
                  <i style={{ width: `${(value / 80) * 100}%` }} />
                </div>
                <div className="stat-left" title={`今日の${label}: あと${left}件まで加算`}>
                  {[0, 1, 2].map((i) => (
                    <span key={i} className={i < left ? "on" : ""} />
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      </header>

      <main className="page">{children}</main>

      {toast && (
        <div key={toast.id} className={`toast ${toast.tone}`} data-stat={toast.stat} role="status">
          {toast.text}
        </div>
      )}

      <nav className="tabbar">
        {NAV.map((n) => (
          <Link key={n.href} href={n.href} className={pathname === n.href ? "active" : ""}>
            {n.label}
          </Link>
        ))}
      </nav>
    </Ctx.Provider>
  );
}

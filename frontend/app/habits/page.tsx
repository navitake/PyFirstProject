"use client";

import { useEffect, useState } from "react";
import { useShell } from "@/components/AppShell";
import CategoryPicker from "@/components/CategoryPicker";
import { api, type Recurring } from "@/lib/api";
import { LABEL, WEEKDAYS, type Stat } from "@/lib/categories";

const ALL_DAYS = [0, 1, 2, 3, 4, 5, 6];

function scheduleLabel(days: number[]) {
  if (days.length === 7) return "毎日";
  if (days.join() === "0,1,2,3,4") return "平日";
  if (days.join() === "5,6") return "土日";
  return `毎週 ${days.map((d) => WEEKDAYS[d]).join("・")}`;
}

function DayPicker({ value, onChange }: { value: number[]; onChange: (v: number[]) => void }) {
  const toggle = (d: number) =>
    onChange(value.includes(d) ? value.filter((x) => x !== d) : [...value, d].sort());
  return (
    <div className="days" role="group" aria-label="繰り返す曜日">
      {WEEKDAYS.map((w, d) => (
        <button
          key={d}
          type="button"
          className={`day ${value.includes(d) ? "on" : ""}`}
          aria-pressed={value.includes(d)}
          onClick={() => toggle(d)}
        >
          {w}
        </button>
      ))}
      <button type="button" className="btn ghost small" onClick={() => onChange(ALL_DAYS)}>
        毎日
      </button>
    </div>
  );
}

export default function HabitsPage() {
  const { notify } = useShell();
  const [rules, setRules] = useState<Recurring[] | null>(null);
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<Stat | null>(null);
  const [days, setDays] = useState<number[]>(ALL_DAYS);

  useEffect(() => {
    api
      .recurring()
      .then(setRules)
      .catch((e) => {
        notify(e.message, "error");
        setRules([]);
      });
  }, [notify]);

  async function add(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    if (!category) return notify("カテゴリを選んでください");
    if (days.length === 0) return notify("曜日を1つ以上選んでください");
    try {
      const r = await api.createRecurring({ title: title.trim(), category, weekdays: days });
      setRules((rs) => [...(rs ?? []), r]);
      setTitle("");
      notify(`「${r.title}」を${scheduleLabel(r.weekdays)}の繰り返しに追加しました`);
    } catch (err) {
      notify((err as Error).message, "error");
    }
  }

  async function setActive(r: Recurring, active: boolean) {
    try {
      const updated = await api.updateRecurring(r.id, { active });
      setRules((rs) => rs?.map((x) => (x.id === r.id ? updated : x)) ?? null);
    } catch (e) {
      notify((e as Error).message, "error");
    }
  }

  async function remove(r: Recurring) {
    if (!confirm(`「${r.title}」の繰り返しを削除しますか？（完了済みの記録は残ります）`)) return;
    try {
      await api.deleteRecurring(r.id);
      setRules((rs) => rs?.filter((x) => x.id !== r.id) ?? null);
    } catch (e) {
      notify((e as Error).message, "error");
    }
  }

  return (
    <>
      <div className="page-head">
        <h1>繰り返し</h1>
      </div>
      <p className="hint">該当する曜日になると「今日」に自動で並びます。やらなかった日の分は翌日に持ち越しません。</p>

      <form className="composer" onSubmit={add}>
        <div className="composer-row">
          <input
            className="input"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="例: 朝ランニング"
            maxLength={200}
            aria-label="繰り返しタスク名"
          />
          <button className="btn primary" disabled={!title.trim()}>
            追加
          </button>
        </div>
        <CategoryPicker value={category} onChange={setCategory} />
        <DayPicker value={days} onChange={setDays} />
      </form>

      {rules === null ? (
        <p className="empty">読み込み中…</p>
      ) : rules.length === 0 ? (
        <p className="empty">繰り返しタスクはまだありません。</p>
      ) : (
        <ul className="tasks">
          {rules.map((r) => (
            <li key={r.id} className={`task habit ${r.active ? "" : "paused"}`} data-stat={r.category}>
              <div className="task-body static">
                <span className="task-title">{r.title}</span>
                <span className="task-meta">
                  <span className="tag" data-stat={r.category}>
                    {LABEL[r.category]}
                  </span>
                  <span className="tag plain">{scheduleLabel(r.weekdays)}</span>
                  {!r.active && <span className="tag plain">停止中</span>}
                </span>
              </div>
              <div className="row-actions">
                <button className="btn ghost small" onClick={() => setActive(r, !r.active)}>
                  {r.active ? "止める" : "再開"}
                </button>
                <button className="btn ghost small danger" onClick={() => remove(r)}>
                  削除
                </button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </>
  );
}

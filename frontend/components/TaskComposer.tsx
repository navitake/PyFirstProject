"use client";

import { useState } from "react";
import { api, type Task } from "@/lib/api";
import type { Stat } from "@/lib/categories";
import CategoryPicker from "./CategoryPicker";
import { useShell } from "./AppShell";

/** タスクの登録フォーム。今日の画面では期限が今日に固定され、すべての画面では期限を選べる。 */
export default function TaskComposer({
  defaultDue,
  allowDue,
  onCreated,
}: {
  defaultDue: string | null;
  allowDue: boolean;
  onCreated: (t: Task) => void;
}) {
  const { notify } = useShell();
  const [title, setTitle] = useState("");
  const [category, setCategory] = useState<Stat | null>(null);
  const [due, setDue] = useState<string>("");
  const [busy, setBusy] = useState(false);

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    if (!category) return notify("カテゴリを選んでください");
    setBusy(true);
    try {
      const task = await api.createTask({
        title: title.trim(),
        category,
        due_date: allowDue ? due || null : defaultDue,
      });
      onCreated(task);
      setTitle("");
      setDue("");
    } catch (err) {
      notify((err as Error).message, "error");
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="composer" onSubmit={submit}>
      <div className="composer-row">
        <input
          className="input"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="タスクを追加"
          maxLength={200}
          aria-label="タスク名"
        />
        <button className="btn primary" disabled={busy || !title.trim()}>
          追加
        </button>
      </div>
      <div className="composer-row wrap">
        <CategoryPicker value={category} onChange={setCategory} />
        {allowDue && (
          <label className="due-field">
            期限
            <input type="date" className="input date" value={due} onChange={(e) => setDue(e.target.value)} />
          </label>
        )}
      </div>
    </form>
  );
}

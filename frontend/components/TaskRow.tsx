"use client";

import { useState } from "react";
import { api, type Task } from "@/lib/api";
import { LABEL, type Stat } from "@/lib/categories";
import CategoryPicker from "./CategoryPicker";
import { useShell } from "./AppShell";

function dueLabel(due: string, today: string | undefined): string {
  if (due === today) return "今日";
  const d = new Date(`${due}T00:00:00`);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}

/** タスク1行。丸を押すと完了／取り消し、タイトルを押すと編集。 */
export default function TaskRow({
  task,
  showDue,
  onChanged,
  onDeleted,
}: {
  task: Task;
  showDue: boolean;
  onChanged: (t: Task) => void;
  onDeleted: (id: number) => void;
}) {
  const { stats, setStats, notify, showGain } = useShell();
  const [editing, setEditing] = useState(false);
  const [title, setTitle] = useState(task.title);
  const [category, setCategory] = useState<Stat>(task.category);
  const [due, setDue] = useState(task.due_date ?? "");
  const done = task.completed_at !== null;

  function startEdit() {
    setTitle(task.title);
    setCategory(task.category);
    setDue(task.due_date ?? "");
    setEditing(true);
  }

  async function toggle() {
    try {
      const r = done ? await api.uncomplete(task.id) : await api.complete(task.id);
      onChanged(r.task);
      if (done) {
        setStats(r.stats);
        notify("完了を取り消しました");
      } else showGain(r);
    } catch (e) {
      notify((e as Error).message, "error");
    }
  }

  async function save() {
    if (!title.trim()) return notify("タスク名を入力してください");
    try {
      const body: Parameters<typeof api.updateTask>[1] = { title: title.trim(), category };
      if (!task.recurring_id) body.due_date = due || null; // 繰り返しの分は期限を変えない
      onChanged(await api.updateTask(task.id, body));
      setEditing(false);
    } catch (e) {
      notify((e as Error).message, "error");
    }
  }

  async function remove() {
    try {
      await api.deleteTask(task.id);
      onDeleted(task.id);
      if (done) api.stats().then(setStats);
    } catch (e) {
      notify((e as Error).message, "error");
    }
  }

  if (editing) {
    return (
      <li className="task editing">
        <input className="input" value={title} onChange={(e) => setTitle(e.target.value)} maxLength={200} autoFocus />
        <CategoryPicker value={category} onChange={setCategory} />
        {!task.recurring_id && (
          <label className="due-field">
            期限
            <input type="date" className="input date" value={due} onChange={(e) => setDue(e.target.value)} />
          </label>
        )}
        <div className="row-actions">
          <button className="btn danger ghost" onClick={remove}>
            削除
          </button>
          <span className="spacer" />
          <button className="btn ghost" onClick={() => setEditing(false)}>
            やめる
          </button>
          <button className="btn primary" onClick={save}>
            保存
          </button>
        </div>
      </li>
    );
  }

  return (
    <li className={`task ${done ? "done" : ""}`} data-stat={task.category}>
      <button
        className="check"
        onClick={toggle}
        aria-label={done ? `「${task.title}」の完了を取り消す` : `「${task.title}」を完了する`}
        aria-pressed={done}
      />
      <button className="task-body" onClick={startEdit} aria-label={`「${task.title}」を編集`}>
        <span className="task-title">{task.title}</span>
        <span className="task-meta">
          <span className="tag" data-stat={task.category}>
            {LABEL[task.category]}
          </span>
          {task.recurring_id && <span className="tag plain">繰り返し</span>}
          {task.overdue && <span className="tag warn">期限切れ {dueLabel(task.due_date!, stats?.today)}</span>}
          {showDue && !task.overdue && task.due_date && (
            <span className="tag plain">{dueLabel(task.due_date, stats?.today)}</span>
          )}
        </span>
      </button>
    </li>
  );
}

"use client";

import { useCallback, useEffect, useState } from "react";
import { useShell } from "@/components/AppShell";
import TaskComposer from "@/components/TaskComposer";
import TaskRow from "@/components/TaskRow";
import { api, type Task } from "@/lib/api";

function formatToday(iso: string) {
  const d = new Date(`${iso}T00:00:00`);
  return `${d.getMonth() + 1}月${d.getDate()}日（${"日月火水木金土"[d.getDay()]}）`;
}

export default function TodayPage() {
  const { stats, setStats, notify } = useShell();
  const [tasks, setTasks] = useState<Task[] | null>(null);

  const load = useCallback(async () => {
    try {
      const r = await api.today();
      setTasks(r.tasks);
      setStats(r.stats);
    } catch (e) {
      notify((e as Error).message, "error");
      setTasks([]);
    }
  }, [setStats, notify]);

  useEffect(() => {
    load();
  }, [load]);

  const replace = (t: Task) => setTasks((ts) => ts?.map((x) => (x.id === t.id ? t : x)) ?? null);
  const remove = (id: number) => setTasks((ts) => ts?.filter((x) => x.id !== id) ?? null);

  const open = tasks?.filter((t) => !t.completed_at) ?? [];
  const done = tasks?.filter((t) => t.completed_at) ?? [];

  return (
    <>
      <div className="page-head">
        <h1>今日</h1>
        {stats && <span className="date num">{formatToday(stats.today)}</span>}
      </div>

      <TaskComposer
        defaultDue={stats?.today ?? null}
        allowDue={false}
        onCreated={(t) => setTasks((ts) => [...(ts ?? []), t])}
      />

      {tasks === null ? (
        <p className="empty">読み込み中…</p>
      ) : open.length === 0 && done.length === 0 ? (
        <p className="empty">今日のタスクはまだありません。上の欄から追加できます。</p>
      ) : (
        <>
          <ul className="tasks">
            {open.map((t) => (
              <TaskRow key={t.id} task={t} showDue={false} onChanged={replace} onDeleted={remove} />
            ))}
          </ul>
          {open.length === 0 && <p className="empty">今日のタスクはすべて完了しました。</p>}
          {done.length > 0 && (
            <>
              <h2 className="section">完了 {done.length}件</h2>
              <ul className="tasks">
                {done.map((t) => (
                  <TaskRow key={t.id} task={t} showDue={false} onChanged={replace} onDeleted={remove} />
                ))}
              </ul>
            </>
          )}
        </>
      )}
    </>
  );
}

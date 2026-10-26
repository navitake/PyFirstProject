"use client";

import { useCallback, useEffect, useState } from "react";
import { useShell } from "@/components/AppShell";
import TaskComposer from "@/components/TaskComposer";
import TaskRow from "@/components/TaskRow";
import { api, type Task } from "@/lib/api";

type Group = { key: string; title: string; tasks: Task[] };

function groupTasks(tasks: Task[], today: string): Group[] {
  const groups: Group[] = [
    { key: "overdue", title: "期限切れ", tasks: [] },
    { key: "today", title: "今日", tasks: [] },
    { key: "later", title: "これから", tasks: [] },
    { key: "none", title: "期限なし", tasks: [] },
  ];
  for (const t of tasks) {
    if (!t.due_date) groups[3].tasks.push(t);
    else if (t.due_date < today) groups[0].tasks.push(t);
    else if (t.due_date === today) groups[1].tasks.push(t);
    else groups[2].tasks.push(t);
  }
  return groups.filter((g) => g.tasks.length > 0);
}

export default function AllTasksPage() {
  const { stats, notify } = useShell();
  const [tasks, setTasks] = useState<Task[] | null>(null);

  const load = useCallback(async () => {
    try {
      setTasks(await api.openTasks());
    } catch (e) {
      notify((e as Error).message, "error");
      setTasks([]);
    }
  }, [notify]);

  useEffect(() => {
    load();
  }, [load]);

  // 完了したタスクはこの画面から外す（「今日」画面の完了一覧に出る）
  const changed = (t: Task) =>
    setTasks((ts) => (t.completed_at ? ts?.filter((x) => x.id !== t.id) : ts?.map((x) => (x.id === t.id ? t : x))) ?? null);
  const remove = (id: number) => setTasks((ts) => ts?.filter((x) => x.id !== id) ?? null);

  return (
    <>
      <div className="page-head">
        <h1>すべて</h1>
        {tasks && <span className="date num">未完了 {tasks.length}件</span>}
      </div>

      <TaskComposer defaultDue={null} allowDue onCreated={() => load()} />

      {tasks === null || !stats ? (
        <p className="empty">読み込み中…</p>
      ) : tasks.length === 0 ? (
        <p className="empty">未完了のタスクはありません。</p>
      ) : (
        groupTasks(tasks, stats.today).map((g) => (
          <section key={g.key}>
            <h2 className={`section ${g.key === "overdue" ? "warn" : ""}`}>
              {g.title} {g.tasks.length}件
            </h2>
            <ul className="tasks">
              {g.tasks.map((t) => (
                <TaskRow key={t.id} task={t} showDue={g.key === "later"} onChanged={changed} onDeleted={remove} />
              ))}
            </ul>
          </section>
        ))
      )}
    </>
  );
}

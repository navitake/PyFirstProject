"use client";

import { CATEGORIES, type Stat } from "@/lib/categories";

export default function CategoryPicker({
  value,
  onChange,
}: {
  value: Stat | null;
  onChange: (s: Stat) => void;
}) {
  return (
    <div className="chips" role="radiogroup" aria-label="カテゴリ">
      {CATEGORIES.map((c) => (
        <button
          key={c.stat}
          type="button"
          role="radio"
          aria-checked={value === c.stat}
          className={`chip ${value === c.stat ? "on" : ""}`}
          data-stat={c.stat}
          title={c.examples}
          onClick={() => onChange(c.stat)}
        >
          {c.label}
        </button>
      ))}
    </div>
  );
}

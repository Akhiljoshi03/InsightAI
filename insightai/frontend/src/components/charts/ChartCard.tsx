import { ReactNode } from "react";

interface Props {
  title: string;
  subtitle?: string;
  children: ReactNode;
}

export default function ChartCard({ title, subtitle, children }: Props) {
  return (
    <div className="bg-panel border border-border rounded-2xl p-5">
      <div className="mb-3">
        <div className="font-display font-semibold text-sm">{title}</div>
        {subtitle && <div className="text-xs text-white/40 mt-0.5 font-mono">{subtitle}</div>}
      </div>
      {children}
    </div>
  );
}

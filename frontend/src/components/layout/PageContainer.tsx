import type { ReactNode } from "react";

interface PageContainerProps {
  title: string;
  subtitle: string;
  actions?: ReactNode;
  children: ReactNode;
}

export default function PageContainer({
  title,
  subtitle,
  actions,
  children,
}: PageContainerProps) {
  return (
    <section className="space-y-6">
      <div className="rounded-3xl border border-white/10 bg-white/5 p-6 shadow-2xl shadow-black/20">
        <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm uppercase tracking-[0.3em] text-sky-300">Catálogo</p>
            <h2 className="mt-2 text-3xl font-bold text-white">{title}</h2>
            <p className="mt-2 max-w-2xl text-sm text-slate-300">{subtitle}</p>
          </div>
          {actions ? <div className="flex gap-3">{actions}</div> : null}
        </div>
      </div>

      {children}
    </section>
  );
}

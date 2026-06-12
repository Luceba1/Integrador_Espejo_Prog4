import type { ReactNode } from "react";

interface ModalProps {
  open: boolean;
  title: string;
  children: ReactNode;
  onClose: () => void;
}

export default function Modal({ open, title, children, onClose }: ModalProps) {
  if (!open) {
    return null;
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-hidden bg-slate-950/70 px-4 py-4 backdrop-blur-sm sm:py-6">
      <div className="flex h-[calc(100vh-2rem)] w-full max-w-3xl flex-col overflow-hidden rounded-3xl border border-white/10 bg-slate-900 shadow-2xl sm:h-[calc(100vh-3rem)]">
        <div className="sticky top-0 z-10 flex items-center justify-between gap-4 rounded-t-3xl border-b border-white/10 bg-slate-900/95 px-6 py-4 backdrop-blur">
          <h3 className="text-xl font-bold text-white">{title}</h3>
          <button
            type="button"
            onClick={onClose}
            className="rounded-full border border-white/10 px-3 py-1 text-sm text-slate-300 hover:bg-white/10"
          >
            Cerrar
          </button>
        </div>
        <div className="flex-1 overflow-y-auto px-6 pb-0 pt-5">
          {children}
        </div>
      </div>
    </div>
  );
}

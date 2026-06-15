import { create } from "zustand";

interface SessionState {
  lastAuthCheckAt: string | null;
  roles: string[];
  setSessionSnapshot: (roles: string[]) => void;
  clearSessionSnapshot: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  lastAuthCheckAt: null,
  roles: [],
  setSessionSnapshot: (roles) =>
    set({
      roles,
      lastAuthCheckAt: new Date().toISOString(),
    }),
  clearSessionSnapshot: () => set({ roles: [], lastAuthCheckAt: null }),
}));

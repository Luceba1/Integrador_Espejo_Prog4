import { create } from "zustand";

interface UiState {
  cartPreviewOpen: boolean;
  lastToast: { type: "success" | "error" | "info"; message: string } | null;
  setCartPreviewOpen: (open: boolean) => void;
  showToast: (type: "success" | "error" | "info", message: string) => void;
  clearToast: () => void;
}

export const useUiStore = create<UiState>((set) => ({
  cartPreviewOpen: false,
  lastToast: null,
  setCartPreviewOpen: (cartPreviewOpen) => set({ cartPreviewOpen }),
  showToast: (type, message) => set({ lastToast: { type, message } }),
  clearToast: () => set({ lastToast: null }),
}));

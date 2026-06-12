import type { ReactNode } from "react";

import { useCarritoStore } from "../stores/carritoStore";

export function CarritoProvider({ children }: { children: ReactNode }) {
  // Zustand no necesita Provider para este store, pero mantenemos este wrapper
  // para no romper la estructura existente del árbol de React.
  return <>{children}</>;
}

export function useCarrito() {
  const items = useCarritoStore((state) => state.items);
  const addProducto = useCarritoStore((state) => state.addProducto);
  const updateCantidad = useCarritoStore((state) => state.updateCantidad);
  const removeItem = useCarritoStore((state) => state.removeItem);
  const clearCart = useCarritoStore((state) => state.clearCart);

  const subtotal = items.reduce((acc, item) => acc + item.precio_unitario * item.cantidad, 0);
  const totalItems = items.reduce((acc, item) => acc + item.cantidad, 0);

  return {
    items,
    totalItems,
    subtotal,
    addProducto,
    updateCantidad,
    removeItem,
    clearCart,
    hasItems: items.length > 0,
  };
}

import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

import type { CarritoItem } from "../types/carrito";
import type { Producto } from "../types/producto";

const STORAGE_KEY = "parcial2_store_carrito";

interface CarritoStoreState {
  items: CarritoItem[];
  addProducto: (producto: Producto, cantidad?: number) => void;
  updateCantidad: (productoId: number, cantidad: number) => void;
  removeItem: (productoId: number) => void;
  clearCart: () => void;
  syncProducto: (producto: Producto) => void;
}

function normalizarItems(items: CarritoItem[]): CarritoItem[] {
  return items.filter((item) => item.producto_id && item.cantidad > 0);
}

export const useCarritoStore = create<CarritoStoreState>()(
  persist(
    (set) => ({
      items: [],

      addProducto: (producto, cantidad = 1) => {
        if (!producto.disponible || producto.stock_cantidad <= 0) return;

        set((state) => {
          const existing = state.items.find((item) => item.producto_id === producto.id);
          const maxCantidad = Math.max(1, producto.stock_cantidad);

          if (existing) {
            return {
              items: state.items.map((item) =>
                item.producto_id === producto.id
                  ? {
                      ...item,
                      cantidad: Math.min(maxCantidad, item.cantidad + cantidad),
                      stock_cantidad: producto.stock_cantidad,
                    }
                  : item
              ),
            };
          }

          return {
            items: [
              ...state.items,
              {
                producto_id: producto.id,
                nombre: producto.nombre,
                precio_unitario: Number(producto.precio_base),
                imagen_url: producto.imagenes_url?.[0] ?? null,
                cantidad: Math.min(maxCantidad, cantidad),
                stock_cantidad: producto.stock_cantidad,
              },
            ],
          };
        });
      },

      updateCantidad: (productoId, cantidad) => {
        set((state) => ({
          items: state.items
            .map((item) =>
              item.producto_id === productoId
                ? {
                    ...item,
                    cantidad: Math.min(Math.max(1, cantidad), Math.max(1, item.stock_cantidad)),
                  }
                : item
            )
            .filter((item) => item.cantidad > 0),
        }));
      },

      removeItem: (productoId) => {
        set((state) => ({
          items: state.items.filter((item) => item.producto_id !== productoId),
        }));
      },

      clearCart: () => set({ items: [] }),

      syncProducto: (producto) => {
        set((state) => ({
          items: state.items
            .map((item) => {
              if (item.producto_id !== producto.id) return item;

              const maxCantidad = Math.max(0, producto.stock_cantidad);
              if (!producto.disponible || maxCantidad <= 0) return null;

              return {
                ...item,
                nombre: producto.nombre,
                precio_unitario: Number(producto.precio_base),
                imagen_url: producto.imagenes_url?.[0] ?? null,
                stock_cantidad: maxCantidad,
                cantidad: Math.min(item.cantidad, maxCantidad),
              };
            })
            .filter((item): item is CarritoItem => item !== null && item.cantidad > 0),
        }));
      },
    }),
    {
      name: STORAGE_KEY,
      storage: createJSONStorage(() => window.localStorage),
      partialize: (state) => ({ items: normalizarItems(state.items) }),
    }
  )
);

import axios, { AxiosError, type AxiosRequestConfig } from "axios";

const API_URL = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";

export const API_BASE_URL = `${API_URL}/api/v1`;

interface FastApiValidationErrorItem {
  loc?: Array<string | number>;
  msg?: string;
}

function normalizeErrorMessage(errorData: unknown, fallback: string): string {
  if (!errorData || typeof errorData !== "object") return fallback;

  const detail = (errorData as { detail?: unknown }).detail;

  if (typeof detail === "string" && detail.trim()) return detail;

  if (Array.isArray(detail)) {
    const messages = detail
      .map((item) => {
        const errorItem = item as FastApiValidationErrorItem;
        const location = Array.isArray(errorItem.loc) ? errorItem.loc.join(" → ") : "campo";
        const message = typeof errorItem.msg === "string" ? errorItem.msg : "valor inválido";
        return `${location}: ${message}`;
      })
      .filter(Boolean);

    if (messages.length) return messages.join(" | ");
  }

  return fallback;
}

export const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use((config) => {
  // El JWT principal viaja en cookie HttpOnly. Este interceptor queda centralizado
  // para futuras extensiones y para cumplir la instancia única de axios del parcial.
  config.withCredentials = true;

  // Si se envía FormData, Axios/navegador debe generar automáticamente
  // el Content-Type multipart/form-data con su boundary.
  // Si dejamos application/json, FastAPI no recibe el campo "files".
  if (config.data instanceof FormData) {
    delete config.headers["Content-Type"];
  }

  return config;
});

let isRefreshing = false;
let refreshQueue: Array<() => void> = [];

function resolveRefreshQueue() {
  refreshQueue.forEach((resolve) => resolve());
  refreshQueue = [];
}

api.interceptors.response.use(
  (response) => response,
  async (error: AxiosError) => {
    const status = error.response?.status;
    const originalRequest = error.config as (AxiosRequestConfig & { _retry?: boolean }) | undefined;

    if (status === 401 && originalRequest && !originalRequest._retry && originalRequest.url !== "/auth/refresh") {
      originalRequest._retry = true;

      if (isRefreshing) {
        await new Promise<void>((resolve) => refreshQueue.push(resolve));
        return api.request(originalRequest);
      }

      try {
        isRefreshing = true;
        await api.post("/auth/refresh");
        resolveRefreshQueue();
        return api.request(originalRequest);
      } catch (refreshError) {
        resolveRefreshQueue();
        const message = normalizeErrorMessage((refreshError as AxiosError).response?.data, "Sesión vencida. Iniciá sesión nuevamente.");
        return Promise.reject(new Error(message));
      } finally {
        isRefreshing = false;
      }
    }

    const fallback = status ? `Error ${status}` : "No se pudo conectar con la API.";
    const message = normalizeErrorMessage(error.response?.data, fallback);
    return Promise.reject(new Error(message));
  }
);

export async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const method = options.method ?? "GET";
  let data: unknown = undefined;

  if (options.body !== undefined && options.body !== null) {
    if (typeof options.body === "string") {
      data = options.body.trim() ? JSON.parse(options.body) : undefined;
    } else {
      data = options.body;
    }
  }

  const config: AxiosRequestConfig = {
    url: path,
    method,
    data,
    headers: options.headers as AxiosRequestConfig["headers"],
  };

  const response = await api.request<T>(config);
  return response.data;
}

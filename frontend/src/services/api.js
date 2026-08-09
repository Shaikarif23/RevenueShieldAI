import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "/api",
  timeout: 15000,
  headers: {
    Accept: "application/json",
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("revenueshield_token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("revenueshield_token");
      localStorage.removeItem("revenueshield_user");
      window.dispatchEvent(new Event("auth-expired"));
    }
    return Promise.reject(error);
  }
);

export default api;

export function getApiError(error, fallback = "Something went wrong.") {
  const detail = error?.response?.data?.detail;
  const message = error?.response?.data?.error;
  if (typeof detail === "string") return detail;
  if (typeof message === "string") return message;
  if (error?.message === "Network Error") {
    return "Cannot reach the backend. Make sure FastAPI is running on port 8000.";
  }
  return fallback;
}
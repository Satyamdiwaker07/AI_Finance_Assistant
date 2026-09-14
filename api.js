import axios from "axios";

export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://localhost:8000",
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem("finance_token");
  if (token) config.headers.Authorization = `Bearer ${token}`;
  return config;
});

export async function request(promise) {
  try {
    const { data } = await promise;
    return data;
  } catch (error) {
    const detail = error.response?.data?.detail;
    throw new Error(typeof detail === "string" ? detail : "Something went wrong.");
  }
}

import axios from "axios";

const configuredBaseUrl = import.meta.env.VITE_API_URL?.trim();

const api = axios.create({
  baseURL: (configuredBaseUrl || "http://localhost:8000").replace(/\/$/, ""),
  timeout: 120000,
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const validationDetail = error?.response?.data?.detail;
    const validationMessage = Array.isArray(validationDetail)
      ? validationDetail.map((item) => item?.msg).filter(Boolean).join(" ")
      : validationDetail;
    const message =
      error?.response?.data?.error ||
      validationMessage ||
      (error?.code === "ECONNABORTED"
        ? "The server took too long to respond. Please try again."
        : null) ||
      (error?.code === "ERR_NETWORK"
        ? `Cannot connect to Saksham API at ${error.config?.baseURL || api.defaults.baseURL}. Start the backend and try again.`
        : null) ||
      error?.message ||
      "Something went wrong. Please try again.";
    return Promise.reject(new Error(message));
  },
);

export default api;

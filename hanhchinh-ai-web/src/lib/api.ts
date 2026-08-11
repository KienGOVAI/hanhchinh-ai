import axios from "axios";

import type {
  AxiosError,
  AxiosInstance,
  AxiosResponse,
} from "axios";

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

const api: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

api.interceptors.request.use(
  (config) => {
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },

  (error: AxiosError) => {
    if (error.response) {
      console.error("API Error:", {
        status: error.response.status,
        data: error.response.data,
      });
    } else if (error.request) {
      console.error(
        "API Network Error:",
        error.message
      );
    } else {
      console.error(
        "API Request Error:",
        error.message
      );
    }

    return Promise.reject(error);
  }
);

export default api;
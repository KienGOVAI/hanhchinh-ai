import axios, {
  AxiosError,
  AxiosInstance,
  AxiosResponse,
} from "axios";

const api: AxiosInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 60000,
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Request Interceptor
 * Tự động thêm JWT sau này.
 */
api.interceptors.request.use(
  (config) => {
    // TODO Sprint Authentication
    // const token = authStore.getState().accessToken;
    //
    // if (token) {
    //   config.headers.Authorization = `Bearer ${token}`;
    // }

    return config;
  },
  (error) => Promise.reject(error)
);

/**
 * Response Interceptor
 */
api.interceptors.response.use(
  (response: AxiosResponse) => response,

  (error: AxiosError) => {
    if (error.response) {
      console.error("API Error:", {
        status: error.response.status,
        data: error.response.data,
      });
    } else if (error.request) {
      console.error("Server không phản hồi.");
    } else {
      console.error(error.message);
    }

    return Promise.reject(error);
  }
);

export default api;
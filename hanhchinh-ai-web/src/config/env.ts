export const env = {
  apiUrl:
    import.meta.env.VITE_API_URL,

  defaultProvider:
    import.meta.env.VITE_DEFAULT_PROVIDER,

  timeout: Number(
    import.meta.env.VITE_REQUEST_TIMEOUT
  ),

  appName:
    import.meta.env.VITE_APP_NAME,

  appVersion:
    import.meta.env.VITE_APP_VERSION,
} as const;
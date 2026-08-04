import { env } from "./env";

export const config = {
  api: {
    baseUrl: env.apiUrl,
    timeout: env.timeout,
  },

  ai: {
    defaultProvider: env.defaultProvider,
  },

  app: {
    name: env.appName,
    version: env.appVersion,
  },
};

export default config;
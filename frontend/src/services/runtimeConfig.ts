export type ArenaFlowConfig = {
  ARENAFLOW_API_BASE_URL: string;
  ARENAFLOW_MAPS_BROWSER_API_KEY: string;
  ARENAFLOW_DEFAULT_LOCALE: string;
  ARENAFLOW_SUPPORTED_LOCALES: string[];
  ARENAFLOW_ENVIRONMENT: string;
  ARENAFLOW_DEFAULT_VENUE_ID: string;
  ARENAFLOW_DEFAULT_EVENT_ID: string;
};

declare global {
  interface Window {
    __ARENAFLOW_CONFIG__?: ArenaFlowConfig;
  }
}

export function getRuntimeConfig(): ArenaFlowConfig {
  return window.__ARENAFLOW_CONFIG__ ?? {
    ARENAFLOW_API_BASE_URL: 'http://localhost:8000',
    ARENAFLOW_MAPS_BROWSER_API_KEY: '',
    ARENAFLOW_DEFAULT_LOCALE: 'en',
    ARENAFLOW_SUPPORTED_LOCALES: ['en', 'es'],
    ARENAFLOW_ENVIRONMENT: 'local',
    ARENAFLOW_DEFAULT_VENUE_ID: '',
    ARENAFLOW_DEFAULT_EVENT_ID: ''
  };
}

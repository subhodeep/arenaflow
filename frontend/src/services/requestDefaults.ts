import { getRuntimeConfig } from './runtimeConfig';

export function baseRequest(language: string, venueId?: string, eventId?: string) {
  const config = getRuntimeConfig();
  return {
    venue_id: venueId || config.ARENAFLOW_DEFAULT_VENUE_ID,
    event_id: eventId || config.ARENAFLOW_DEFAULT_EVENT_ID || undefined,
    language
  };
}

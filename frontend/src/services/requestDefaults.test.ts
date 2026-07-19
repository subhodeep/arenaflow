import { afterEach, describe, expect, it } from 'vitest';
import { baseRequest } from './requestDefaults';

describe('baseRequest', () => {
  afterEach(() => {
    window.__ARENAFLOW_CONFIG__ = undefined;
  });

  it('uses explicit venue and event values when provided', () => {
    expect(baseRequest('es', 'venue-1', 'event-1')).toEqual({
      venue_id: 'venue-1',
      event_id: 'event-1',
      language: 'es'
    });
  });

  it('falls back to runtime defaults', () => {
    window.__ARENAFLOW_CONFIG__ = {
      ARENAFLOW_API_BASE_URL: 'https://api.example',
      ARENAFLOW_MAPS_BROWSER_API_KEY: '',
      ARENAFLOW_DEFAULT_LOCALE: 'en',
      ARENAFLOW_SUPPORTED_LOCALES: ['en', 'es'],
      ARENAFLOW_ENVIRONMENT: 'test',
      ARENAFLOW_DEFAULT_VENUE_ID: 'default-venue',
      ARENAFLOW_DEFAULT_EVENT_ID: 'default-event'
    };

    expect(baseRequest('en')).toEqual({
      venue_id: 'default-venue',
      event_id: 'default-event',
      language: 'en'
    });
  });
});

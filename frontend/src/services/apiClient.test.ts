import { afterEach, describe, expect, it, vi } from 'vitest';
import { postJson } from './apiClient';

const fetchMock = vi.fn();
globalThis.fetch = fetchMock;

describe('postJson', () => {
  afterEach(() => {
    fetchMock.mockReset();
    window.__ARENAFLOW_CONFIG__ = undefined;
  });

  it('posts JSON to the configured API base URL', async () => {
    window.__ARENAFLOW_CONFIG__ = {
      ARENAFLOW_API_BASE_URL: 'https://api.example',
      ARENAFLOW_MAPS_BROWSER_API_KEY: '',
      ARENAFLOW_DEFAULT_LOCALE: 'en',
      ARENAFLOW_SUPPORTED_LOCALES: ['en'],
      ARENAFLOW_ENVIRONMENT: 'test',
      ARENAFLOW_DEFAULT_VENUE_ID: 'venue',
      ARENAFLOW_DEFAULT_EVENT_ID: 'event'
    };
    fetchMock.mockResolvedValue({ ok: true, json: async () => ({ answer: 'ok' }) });

    const result = await postJson('/api/v1/assistant/chat', { message: 'hello' }, 'staff-token');

    expect(result).toEqual({ answer: 'ok' });
    expect(fetchMock).toHaveBeenCalledWith('https://api.example/api/v1/assistant/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: 'Bearer staff-token'
      },
      body: JSON.stringify({ message: 'hello' })
    });
  });

  it('throws the backend error message when a request fails', async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      json: async () => ({ error: { message: 'Request validation failed.' } })
    });

    await expect(postJson('/api/v1/assistant/chat', {})).rejects.toThrow(
      'Request validation failed.'
    );
  });
});

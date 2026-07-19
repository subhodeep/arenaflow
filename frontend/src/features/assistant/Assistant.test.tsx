import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { afterEach, describe, expect, it, vi } from 'vitest';
import { Assistant } from './Assistant';

const fetchMock = vi.fn();
globalThis.fetch = fetchMock;

describe('Assistant', () => {
  afterEach(() => {
    fetchMock.mockReset();
    window.__ARENAFLOW_CONFIG__ = undefined;
  });

  it('submits a fan question and renders the response', async () => {
    fetchMock.mockResolvedValue({
      ok: true,
      json: async () => ({
        answer: 'Use Gate A for accessible entry.',
        confidence: 'high',
        language: 'en',
        suggested_actions: ['Follow blue accessibility signs']
      })
    });
    render(<Assistant language="en" venueId="demo-venue" />);

    await userEvent.clear(screen.getByLabelText('Question'));
    await userEvent.type(screen.getByLabelText('Question'), 'Where is accessible entry?');
    await userEvent.click(screen.getByRole('button', { name: 'Ask ArenaFlow' }));

    await waitFor(() => {
      expect(screen.getByText('Use Gate A for accessible entry.')).toBeInTheDocument();
    });
    expect(screen.getByText('Follow blue accessibility signs')).toBeInTheDocument();
    expect(fetchMock).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/assistant/chat',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({
          venue_id: 'demo-venue',
          event_id: undefined,
          language: 'en',
          message: 'Where is accessible entry?',
          user_type: 'fan'
        })
      })
    );
  });
});

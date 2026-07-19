import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { ResultCard } from './ResultCard';

describe('ResultCard', () => {
  it('renders nothing before a result or error exists', () => {
    const { container } = render(<ResultCard title="Assistant response" />);

    expect(container).toBeEmptyDOMElement();
  });

  it('renders response summaries, metadata, and nested lists', () => {
    render(
      <ResultCard
        title="Operational intelligence"
        tone="ops"
        result={{
          recommendation: 'Open overflow route after staff confirmation.',
          confidence: 'high',
          language: 'en',
          priority: 'critical',
          action_cards: [
            {
              title: 'Dispatch staff observer',
              steps: ['Confirm exits remain clear'],
              accessibility_notes: ['Keep step-free route open']
            }
          ],
          assumptions: ['Crowd data is current'],
          safety_notes: ['Escalate blocked egress immediately']
        }}
      />
    );

    expect(screen.getByText('Open overflow route after staff confirmation.')).toBeInTheDocument();
    expect(screen.getByText('Confidence')).toBeInTheDocument();
    expect(screen.getByText('critical')).toBeInTheDocument();
    expect(screen.getByText('Dispatch staff observer')).toBeInTheDocument();
    expect(screen.getByText('Confirm exits remain clear')).toBeInTheDocument();
    expect(screen.getByText('Keep step-free route open')).toBeInTheDocument();
  });

  it('renders accessible error state', () => {
    render(<ResultCard title="Assistant response" error="Request failed" />);

    expect(screen.getByText('Action needed')).toBeInTheDocument();
    expect(screen.getByText('Request failed')).toBeInTheDocument();
  });
});

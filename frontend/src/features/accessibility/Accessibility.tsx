import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { useApiMutation } from '../../hooks/useApiMutation';
import { baseRequest } from '../../services/requestDefaults';
import { AccessibilityPlanResponse } from '../../types/api';

type Props = { language: string; venueId: string };

function parseNeeds(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

export function Accessibility({ language, venueId }: Props) {
  const [needs, setNeeds] = useState('wheelchair, step-free, low-sensory');
  const accessibility = useApiMutation<AccessibilityPlanResponse>();

  async function submit(event: FormEvent) {
    event.preventDefault();
    await accessibility.run('/api/v1/accessibility/plan', {
      ...baseRequest(language, venueId),
      origin: 'Gate A',
      destination: 'Section 120',
      needs: parseNeeds(needs),
      companion_count: 1
    });
  }

  return (
    <section className="panel">
      <h2>Accessibility</h2>
      <form onSubmit={submit}>
        <label htmlFor="needs">Needs</label>
        <input id="needs" value={needs} onChange={(event) => setNeeds(event.target.value)} />
        <button type="submit">Create accessibility plan</button>
      </form>
      <ResultCard
        title="Accessibility plan"
        result={accessibility.result}
        error={accessibility.error}
        tone="access"
      />
    </section>
  );
}

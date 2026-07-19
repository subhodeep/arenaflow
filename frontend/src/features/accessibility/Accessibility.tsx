import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { postJson } from '../../services/apiClient';
import { baseRequest } from '../../services/requestDefaults';

type Props = { language: string; venueId: string };

function parseNeeds(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

export function Accessibility({ language, venueId }: Props) {
  const [needs, setNeeds] = useState('wheelchair, step-free, low-sensory');
  const [result, setResult] = useState<unknown>();
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      setResult(
        await postJson('/api/v1/accessibility/plan', {
          ...baseRequest(language, venueId),
          origin: 'Gate A',
          destination: 'Section 120',
          needs: parseNeeds(needs),
          companion_count: 1
        })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    }
  }

  return (
    <section className="panel">
      <h2>Accessibility</h2>
      <form onSubmit={submit}>
        <label htmlFor="needs">Needs</label>
        <input id="needs" value={needs} onChange={(event) => setNeeds(event.target.value)} />
        <button type="submit">Create accessibility plan</button>
      </form>
      <ResultCard title="Accessibility plan" result={result} error={error} tone="access" />
    </section>
  );
}

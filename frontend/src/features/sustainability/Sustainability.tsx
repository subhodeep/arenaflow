import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { postJson } from '../../services/apiClient';
import { baseRequest } from '../../services/requestDefaults';

type Props = { language: string; venueId: string };

export function Sustainability({ language, venueId }: Props) {
  const [intent, setIntent] = useState('water');
  const [result, setResult] = useState<unknown>();
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      setResult(
        await postJson('/api/v1/sustainability/advice', {
          ...baseRequest(language, venueId),
          intent,
          location: 'main concourse',
          preferences: ['low-carbon', 'refill']
        })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    }
  }

  return (
    <section className="panel">
      <h2>Sustainability</h2>
      <form onSubmit={submit}>
        <label htmlFor="intent">Intent</label>
        <select id="intent" value={intent} onChange={(event) => setIntent(event.target.value)}>
          <option value="water">Water refill</option>
          <option value="waste">Waste sorting</option>
          <option value="route">Low-carbon route</option>
          <option value="general">General</option>
        </select>
        <button type="submit">Get sustainability advice</button>
      </form>
      <ResultCard title="Sustainability advice" result={result} error={error} tone="green" />
    </section>
  );
}

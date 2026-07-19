import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { postJson } from '../../services/apiClient';
import { baseRequest } from '../../services/requestDefaults';

type Props = { language: string; venueId: string };

export function Operations({ language, venueId }: Props) {
  const [token, setToken] = useState('');
  const [situation, setSituation] = useState(
    'Gate B queues are increasing and accessible route access may be constrained.'
  );
  const [result, setResult] = useState<unknown>();
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      setResult(
        await postJson(
          '/api/v1/ops/decision-support',
          {
            ...baseRequest(language, venueId),
            situation,
            decision_window_minutes: 15,
            include_sustainability: true,
            include_transportation: true
          },
          token
        )
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    }
  }

  return (
    <section className="panel staff-panel">
      <h2>Operations dashboard</h2>
      <p>Staff-only endpoints require a bearer token outside local bypass mode.</p>
      <form onSubmit={submit}>
        <label htmlFor="staff-token">Staff token</label>
        <input
          id="staff-token"
          type="password"
          value={token}
          onChange={(event) => setToken(event.target.value)}
          autoComplete="off"
        />
        <label htmlFor="situation">Situation</label>
        <textarea
          id="situation"
          value={situation}
          onChange={(event) => setSituation(event.target.value)}
        />
        <button type="submit">Generate decision support</button>
      </form>
      <ResultCard title="Operational intelligence" result={result} error={error} tone="ops" />
    </section>
  );
}

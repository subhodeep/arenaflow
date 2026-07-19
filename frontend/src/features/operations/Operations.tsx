import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { useApiMutation } from '../../hooks/useApiMutation';
import { baseRequest } from '../../services/requestDefaults';
import { OpsDecisionSupportResponse } from '../../types/api';

type Props = { language: string; venueId: string };

export function Operations({ language, venueId }: Props) {
  const [token, setToken] = useState('');
  const [situation, setSituation] = useState(
    'Gate B queues are increasing and accessible route access may be constrained.'
  );
  const operations = useApiMutation<OpsDecisionSupportResponse>();

  async function submit(event: FormEvent) {
    event.preventDefault();
    await operations.run(
      '/api/v1/ops/decision-support',
      {
        ...baseRequest(language, venueId),
        situation,
        decision_window_minutes: 15,
        include_sustainability: true,
        include_transportation: true
      },
      token
    );
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
      <ResultCard
        title="Operational intelligence"
        result={operations.result}
        error={operations.error}
        tone="ops"
      />
    </section>
  );
}

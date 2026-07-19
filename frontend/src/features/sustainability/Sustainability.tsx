import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { useApiMutation } from '../../hooks/useApiMutation';
import { baseRequest } from '../../services/requestDefaults';
import { SustainabilityAdviceResponse } from '../../types/api';

type Props = { language: string; venueId: string };

export function Sustainability({ language, venueId }: Props) {
  const [intent, setIntent] = useState('water');
  const sustainability = useApiMutation<SustainabilityAdviceResponse>();

  async function submit(event: FormEvent) {
    event.preventDefault();
    await sustainability.run('/api/v1/sustainability/advice', {
      ...baseRequest(language, venueId),
      intent,
      location: 'main concourse',
      preferences: ['low-carbon', 'refill']
    });
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
      <ResultCard
        title="Sustainability advice"
        result={sustainability.result}
        error={sustainability.error}
        tone="green"
      />
    </section>
  );
}

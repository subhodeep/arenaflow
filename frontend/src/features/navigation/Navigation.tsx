import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { postJson } from '../../services/apiClient';
import { baseRequest } from '../../services/requestDefaults';
import { StadiumMap } from './StadiumMap';

type Props = { language: string; venueId: string };

export function Navigation({ language, venueId }: Props) {
  const [origin, setOrigin] = useState('Gate A');
  const [destination, setDestination] = useState('Section 120');
  const [result, setResult] = useState<unknown>();
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      setResult(
        await postJson('/api/v1/navigation/route', {
          ...baseRequest(language, venueId),
          origin,
          destination,
          mobility_needs: ['step-free'],
          avoid_crowds: true
        })
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    }
  }

  return (
    <section className="panel">
      <h2>Navigation</h2>
      <div className="navigation-layout">
        <div>
          <p className="feature-intro">
            Plan a step-free, crowd-aware route without exposing browser map API keys. The visual
            preview uses a secure venue floorplan-style overlay.
          </p>
          <form onSubmit={submit}>
            <label htmlFor="origin">Origin</label>
            <input id="origin" value={origin} onChange={(event) => setOrigin(event.target.value)} />
            <label htmlFor="destination">Destination</label>
            <input
              id="destination"
              value={destination}
              onChange={(event) => setDestination(event.target.value)}
            />
            <button type="submit">Plan route</button>
          </form>
        </div>
        <StadiumMap origin={origin} destination={destination} hasResult={Boolean(result)} />
      </div>
      <ResultCard title="Route recommendation" result={result} error={error} tone="fan" />
    </section>
  );
}

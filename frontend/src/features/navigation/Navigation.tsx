import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { useApiMutation } from '../../hooks/useApiMutation';
import { baseRequest } from '../../services/requestDefaults';
import { NavigationRouteResponse } from '../../types/api';
import { StadiumMap } from './StadiumMap';

type Props = { language: string; venueId: string };

export function Navigation({ language, venueId }: Props) {
  const [origin, setOrigin] = useState('Gate A');
  const [destination, setDestination] = useState('Section 120');
  const navigation = useApiMutation<NavigationRouteResponse>();

  async function submit(event: FormEvent) {
    event.preventDefault();
    await navigation.run('/api/v1/navigation/route', {
      ...baseRequest(language, venueId),
      origin,
      destination,
      mobility_needs: ['step-free'],
      avoid_crowds: true
    });
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
        <StadiumMap
          origin={origin}
          destination={destination}
          hasResult={Boolean(navigation.result)}
        />
      </div>
      <ResultCard
        title="Route recommendation"
        result={navigation.result}
        error={navigation.error}
        tone="fan"
      />
    </section>
  );
}

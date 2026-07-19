import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { useApiMutation } from '../../hooks/useApiMutation';
import { baseRequest } from '../../services/requestDefaults';
import { TransportationOptionsResponse } from '../../types/api';

type Props = { language: string; venueId: string };

export function Transportation({ language, venueId }: Props) {
  const [originAddress, setOriginAddress] = useState('Downtown transit hub');
  const transportation = useApiMutation<TransportationOptionsResponse>();

  async function submit(event: FormEvent) {
    event.preventDefault();
    await transportation.run('/api/v1/transportation/options', {
      ...baseRequest(language, venueId),
      origin_address: originAddress,
      departure_context: 'pre_match',
      needs_accessible_transport: true
    });
  }

  return (
    <section className="panel">
      <h2>Transportation</h2>
      <form onSubmit={submit}>
        <label htmlFor="origin-address">Origin address</label>
        <input
          id="origin-address"
          value={originAddress}
          onChange={(event) => setOriginAddress(event.target.value)}
        />
        <button type="submit">Find transportation</button>
      </form>
      <ResultCard
        title="Transportation options"
        result={transportation.result}
        error={transportation.error}
        tone="fan"
      />
    </section>
  );
}

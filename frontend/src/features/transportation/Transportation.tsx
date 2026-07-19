import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { postJson } from '../../services/apiClient';
import { baseRequest } from '../../services/requestDefaults';

type Props = { language: string; venueId: string };

export function Transportation({ language, venueId }: Props) {
  const [originAddress, setOriginAddress] = useState('Downtown transit hub');
  const [result, setResult] = useState<unknown>();
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      setResult(await postJson('/api/v1/transportation/options', { ...baseRequest(language, venueId), origin_address: originAddress, departure_context: 'pre_match', needs_accessible_transport: true }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    }
  }

  return (
    <section className="panel">
      <h2>Transportation</h2>
      <form onSubmit={submit}>
        <label htmlFor="origin-address">Origin address</label>
        <input id="origin-address" value={originAddress} onChange={(event) => setOriginAddress(event.target.value)} />
        <button type="submit">Find transportation</button>
      </form>
      <ResultCard title="Transportation options" result={result} error={error} tone="fan" />
    </section>
  );
}

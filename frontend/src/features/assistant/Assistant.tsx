import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { postJson } from '../../services/apiClient';
import { baseRequest } from '../../services/requestDefaults';

type Props = { language: string; venueId: string };

export function Assistant({ language, venueId }: Props) {
  const [message, setMessage] = useState('Where is the nearest accessible entrance?');
  const [result, setResult] = useState<unknown>();
  const [error, setError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();
    setError(null);
    try {
      setResult(await postJson('/api/v1/assistant/chat', { ...baseRequest(language, venueId), message, user_type: 'fan' }));
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
    }
  }

  return (
    <section className="panel">
      <h2>Multilingual assistant</h2>
      <form onSubmit={submit}>
        <label htmlFor="assistant-message">Question</label>
        <textarea id="assistant-message" value={message} onChange={(event) => setMessage(event.target.value)} />
        <button type="submit">Ask ArenaFlow</button>
      </form>
      <ResultCard title="Assistant response" result={result} error={error} tone="fan" />
    </section>
  );
}

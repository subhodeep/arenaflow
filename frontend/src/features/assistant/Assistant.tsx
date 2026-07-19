import { FormEvent, useState } from 'react';
import { ResultCard } from '../../components/ResultCard';
import { useApiMutation } from '../../hooks/useApiMutation';
import { baseRequest } from '../../services/requestDefaults';
import { AssistantChatResponse } from '../../types/api';

type Props = { language: string; venueId: string };

export function Assistant({ language, venueId }: Props) {
  const [message, setMessage] = useState('Where is the nearest accessible entrance?');
  const assistant = useApiMutation<AssistantChatResponse>();

  async function submit(event: FormEvent) {
    event.preventDefault();
    await assistant.run('/api/v1/assistant/chat', {
      ...baseRequest(language, venueId),
      message,
      user_type: 'fan'
    });
  }

  return (
    <section className="panel">
      <h2>Multilingual assistant</h2>
      <form onSubmit={submit}>
        <label htmlFor="assistant-message">Question</label>
        <textarea
          id="assistant-message"
          value={message}
          onChange={(event) => setMessage(event.target.value)}
        />
        <button type="submit">Ask ArenaFlow</button>
      </form>
      <ResultCard
        title="Assistant response"
        result={assistant.result}
        error={assistant.error}
        tone="fan"
      />
    </section>
  );
}

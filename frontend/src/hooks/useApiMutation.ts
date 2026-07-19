import { useState } from 'react';
import { postJson } from '../services/apiClient';

export function useApiMutation<TResponse>() {
  const [result, setResult] = useState<TResponse>();
  const [error, setError] = useState<string | null>(null);

  async function run<TRequest>(path: string, body: TRequest, token?: string) {
    setError(null);
    try {
      const response = await postJson<TRequest, TResponse>(path, body, token);
      setResult(response);
      return response;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Request failed');
      return undefined;
    }
  }

  return { result, error, run };
}

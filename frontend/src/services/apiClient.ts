import { getRuntimeConfig } from './runtimeConfig';

export type ApiError = {
  error: {
    code: string;
    message: string;
    request_id: string;
  };
};

export async function postJson<TRequest, TResponse>(path: string, body: TRequest, token?: string): Promise<TResponse> {
  const config = getRuntimeConfig();
  const response = await fetch(`${config.ARENAFLOW_API_BASE_URL}${path}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {})
    },
    body: JSON.stringify(body)
  });
  if (!response.ok) {
    const error = (await response.json().catch(() => ({ error: { message: 'Request failed' } }))) as ApiError;
    throw new Error(error.error?.message || 'Request failed');
  }
  return (await response.json()) as TResponse;
}

export function asString(value: unknown): string | undefined {
  if (typeof value === 'string' && value.trim()) return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return undefined;
}

export function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .map((item) => {
      if (typeof item === 'string') return item;
      if (isRecord(item)) {
        return (
          asString(item.title) ||
          asString(item.summary) ||
          asString(item.instruction) ||
          asString(item.recommendation)
        );
      }
      return undefined;
    })
    .filter((item): item is string => Boolean(item));
}

export function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

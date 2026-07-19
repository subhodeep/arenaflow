import { RenderableResult } from './types';

function metaItems(result: RenderableResult) {
  const estimatedMinutes = result.estimated_total_minutes;
  return [
    ['Confidence', result.confidence],
    ['Language', result.language],
    ['Estimated time', estimatedMinutes ? `${estimatedMinutes} min` : undefined],
    ['Priority', result.priority]
  ].filter(([, value]) => Boolean(value));
}

export function ResultMetadata({ result }: { result: RenderableResult }) {
  const meta = metaItems(result);
  if (!meta.length) return null;

  return (
    <div className="meta-grid">
      {meta.map(([label, value]) => (
        <div className="meta-pill" key={label}>
          <span>{label}</span>
          <strong>{value}</strong>
        </div>
      ))}
    </div>
  );
}

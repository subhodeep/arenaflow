type ResultCardProps = {
  title: string;
  result?: unknown;
  error?: string | null;
  tone?: 'fan' | 'ops' | 'green' | 'access';
};

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === 'object' && value !== null && !Array.isArray(value);
}

function asString(value: unknown): string | undefined {
  if (typeof value === 'string' && value.trim()) return value;
  if (typeof value === 'number' || typeof value === 'boolean') return String(value);
  return undefined;
}

function asStringList(value: unknown): string[] {
  if (!Array.isArray(value)) return [];
  return value
    .map((item) => {
      if (typeof item === 'string') return item;
      if (isRecord(item)) {
        return asString(item.title) || asString(item.summary) || asString(item.instruction) || asString(item.recommendation);
      }
      return undefined;
    })
    .filter((item): item is string => Boolean(item));
}

function getPrimaryText(data: Record<string, unknown>): string {
  return (
    asString(data.answer) ||
    asString(data.recommendation) ||
    asString(data.escalation_guidance) ||
    'ArenaFlow generated a response. Review the details below.'
  );
}

function getMeta(data: Record<string, unknown>) {
  return [
    ['Confidence', asString(data.confidence)],
    ['Language', asString(data.language)],
    ['Estimated time', asString(data.estimated_total_minutes) ? `${asString(data.estimated_total_minutes)} min` : undefined],
    ['Priority', asString(data.priority)]
  ].filter(([, value]) => Boolean(value));
}

function renderObjectList(value: unknown, title: string) {
  if (!Array.isArray(value) || value.length === 0) return null;
  return (
    <div className="summary-section">
      <h4>{title}</h4>
      <div className="step-list">
        {value.map((item, index) => {
          if (!isRecord(item)) return <p key={index}>{String(item)}</p>;
          const heading = asString(item.title) || asString(item.mode) || asString(item.instruction) || `Item ${index + 1}`;
          const body = asString(item.summary) || asString(item.recommendation);
          const steps = asStringList(item.steps);
          const notes = [...asStringList(item.accessibility_notes), ...asStringList(item.crowd_notes)];
          return (
            <article className="action-item" key={index}>
              <strong>{heading}</strong>
              {body ? <p>{body}</p> : null}
              {steps.length ? <ul>{steps.map((step) => <li key={step}>{step}</li>)}</ul> : null}
              {notes.length ? <p className="muted">{notes.join(' • ')}</p> : null}
            </article>
          );
        })}
      </div>
    </div>
  );
}

function renderList(value: unknown, title: string, icon: string) {
  const items = asStringList(value);
  if (!items.length) return null;
  return (
    <div className="summary-section">
      <h4>{icon} {title}</h4>
      <ul className="polished-list">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}

export function ResultCard({ title, result, error, tone = 'fan' }: ResultCardProps) {
  if (!result && !error) return null;

  if (error) {
    return (
      <section className="result-card error-card" aria-live="polite">
        <p className="result-kicker">Action needed</p>
        <h3>{title}</h3>
        <p className="error">{error}</p>
      </section>
    );
  }

  if (!isRecord(result)) {
    return (
      <section className={`result-card tone-${tone}`} aria-live="polite">
        <h3>{title}</h3>
        <p>{String(result)}</p>
      </section>
    );
  }

  const meta = getMeta(result);

  return (
    <section className={`result-card tone-${tone}`} aria-live="polite">
      <p className="result-kicker">ArenaFlow recommendation</p>
      <h3>{title}</h3>
      <div className="answer-bubble">
        <p>{getPrimaryText(result)}</p>
      </div>

      {meta.length ? (
        <div className="meta-grid">
          {meta.map(([label, value]) => (
            <div className="meta-pill" key={label}>
              <span>{label}</span>
              <strong>{value}</strong>
            </div>
          ))}
        </div>
      ) : null}

      {renderObjectList(result.route_steps, 'Recommended route steps')}
      {renderObjectList(result.options, 'Best transportation options')}
      {renderObjectList(result.action_cards, 'Operational action cards')}
      {renderList(result.suggested_actions, 'Suggested next steps', '✨')}
      {renderList(result.actions, 'Recommended actions', '✅')}
      {renderList(result.assistance_points, 'Assistance points', '♿')}
      {renderList(result.alternatives, 'Alternatives', '🔁')}
      {renderList(result.assumptions, 'Assumptions', 'ℹ️')}
      {renderList(result.safety_notes, 'Safety notes', '🛡️')}
      {renderList(result.grounding_summary, 'Data grounding', '📡')}

      <details className="raw-details">
        <summary>View technical response</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </section>
  );
}

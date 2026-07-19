import { asString, asStringList, isRecord } from './resultExtractors';

export function ResultObjectList({ value, title }: { value?: unknown[]; title: string }) {
  if (!value?.length) return null;
  return (
    <div className="summary-section">
      <h4>{title}</h4>
      <div className="step-list">
        {value.map((item, index) => {
          if (!isRecord(item)) return <p key={index}>{String(item)}</p>;
          const heading =
            asString(item.title) ||
            asString(item.mode) ||
            asString(item.instruction) ||
            `Item ${index + 1}`;
          const body = asString(item.summary) || asString(item.recommendation);
          const steps = asStringList(item.steps);
          const notes = [
            ...asStringList(item.accessibility_notes),
            ...asStringList(item.crowd_notes)
          ];
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

import { ResultMetadata } from './ResultMetadata';
import { ResultObjectList } from './ResultObjectList';
import { ResultSection } from './ResultSection';
import { RenderableResult, ResultCardProps } from './types';

function primaryText(result: RenderableResult): string {
  return (
    result.answer ||
    result.recommendation ||
    result.escalation_guidance ||
    'ArenaFlow generated a response. Review the details below.'
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

  if (!result) return null;

  return (
    <section className={`result-card tone-${tone}`} aria-live="polite">
      <p className="result-kicker">ArenaFlow recommendation</p>
      <h3>{title}</h3>
      <div className="answer-bubble">
        <p>{primaryText(result)}</p>
      </div>

      <ResultMetadata result={result} />
      <ResultObjectList value={result.route_steps} title="Recommended route steps" />
      <ResultObjectList value={result.options} title="Best transportation options" />
      <ResultObjectList value={result.action_cards} title="Operational action cards" />
      <ResultSection title="Suggested next steps" icon="✨" items={result.suggested_actions} />
      <ResultSection title="Recommended actions" icon="✅" items={result.actions} />
      <ResultSection title="Assistance points" icon="♿" items={result.assistance_points} />
      <ResultSection title="Alternatives" icon="🔁" items={result.alternatives} />
      <ResultSection title="Assumptions" icon="ℹ️" items={result.assumptions} />
      <ResultSection title="Safety notes" icon="🛡️" items={result.safety_notes} />
      <ResultSection title="Data grounding" icon="📡" items={result.grounding_summary} />

      <details className="raw-details">
        <summary>View technical response</summary>
        <pre>{JSON.stringify(result, null, 2)}</pre>
      </details>
    </section>
  );
}

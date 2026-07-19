type ResultSectionProps = {
  title: string;
  icon: string;
  items?: string[];
};

export function ResultSection({ title, icon, items }: ResultSectionProps) {
  if (!items?.length) return null;
  return (
    <div className="summary-section">
      <h4>{icon} {title}</h4>
      <ul className="polished-list">
        {items.map((item) => <li key={item}>{item}</li>)}
      </ul>
    </div>
  );
}

export function GateLabels() {
  return (
    <>
      <g className="gate-label">
        <rect x="42" y="226" width="106" height="44" rx="18" fill="#ffffff" />
        <text x="95" y="253" textAnchor="middle">Gate A</text>
      </g>
      <g className="gate-label">
        <rect x="610" y="198" width="112" height="44" rx="18" fill="#ffffff" />
        <text x="666" y="225" textAnchor="middle">Sec 120</text>
      </g>
      <g className="gate-label gate-label--soft">
        <rect x="320" y="63" width="120" height="38" rx="16" fill="#ffffff" />
        <text x="380" y="87" textAnchor="middle">North Fan Zone</text>
      </g>
      <g className="gate-label gate-label--soft">
        <rect x="300" y="421" width="160" height="38" rx="16" fill="#ffffff" />
        <text x="380" y="445" textAnchor="middle">Transit Plaza</text>
      </g>
    </>
  );
}

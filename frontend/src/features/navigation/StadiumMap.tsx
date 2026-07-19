type StadiumMapProps = {
  origin: string;
  destination: string;
  hasResult: boolean;
};

function shortLabel(value: string) {
  return value.trim() || 'Select point';
}

function StadiumShell() {
  return (
    <>
      <rect x="18" y="18" width="724" height="484" rx="54" fill="#081d2a" />
      <ellipse
        cx="380"
        cy="260"
        rx="325"
        ry="205"
        fill="#102f43"
        stroke="#7dd3fc"
        strokeOpacity="0.34"
        strokeWidth="6"
      />
      <ellipse
        cx="380"
        cy="260"
        rx="268"
        ry="162"
        fill="#173f54"
        stroke="#ffffff"
        strokeOpacity="0.18"
        strokeWidth="3"
      />
      <ellipse
        cx="380"
        cy="260"
        rx="210"
        ry="124"
        fill="#0d2b3b"
        stroke="#ffffff"
        strokeOpacity="0.14"
        strokeWidth="2"
      />
    </>
  );
}

function Pitch() {
  return (
    <>
      <rect
        x="268"
        y="188"
        width="224"
        height="144"
        rx="18"
        fill="url(#pitchGradient)"
        stroke="#d1fae5"
        strokeOpacity="0.8"
        strokeWidth="3"
      />
      <line x1="380" y1="188" x2="380" y2="332" stroke="#d1fae5" strokeOpacity="0.7" />
      <circle cx="380" cy="260" r="31" fill="none" stroke="#d1fae5" strokeOpacity="0.74" />
      <rect x="268" y="224" width="42" height="72" fill="none" stroke="#d1fae5" />
      <rect x="450" y="224" width="42" height="72" fill="none" stroke="#d1fae5" />
    </>
  );
}

function CrowdBands() {
  return (
    <>
      <path
        d="M112 92 C190 58 285 46 380 47 C480 48 574 62 648 98"
        fill="none"
        stroke="#38bdf8"
        strokeOpacity="0.28"
        strokeWidth="28"
        strokeLinecap="round"
      />
      <path
        d="M112 428 C190 462 285 474 380 473 C480 472 574 458 648 422"
        fill="none"
        stroke="#38bdf8"
        strokeOpacity="0.22"
        strokeWidth="28"
        strokeLinecap="round"
      />
      <path
        d="M73 178 C52 230 52 290 75 342"
        fill="none"
        stroke="#f97316"
        strokeOpacity="0.36"
        strokeWidth="30"
        strokeLinecap="round"
      />
      <path
        d="M687 178 C708 230 708 290 685 342"
        fill="none"
        stroke="#f43f5e"
        strokeOpacity="0.34"
        strokeWidth="30"
        strokeLinecap="round"
      />
    </>
  );
}

function AccessibleRoute({ hasResult }: Pick<StadiumMapProps, 'hasResult'>) {
  const routePath = 'M95 260 C160 338 250 374 350 356 C462 336 542 274 665 228';
  return (
    <>
      <path
        className={hasResult ? 'route-line route-line--active' : 'route-line'}
        d={routePath}
        fill="none"
        stroke="url(#routeGradient)"
        strokeWidth="13"
        strokeLinecap="round"
        strokeDasharray="18 14"
        filter="url(#routeGlow)"
      />
      <path
        d={routePath}
        fill="none"
        stroke="#ffffff"
        strokeOpacity="0.65"
        strokeWidth="2"
        strokeLinecap="round"
        strokeDasharray="2 24"
      />
    </>
  );
}

function MapMarkers() {
  return (
    <>
      <g className="map-marker map-marker--origin" transform="translate(95 260)">
        <circle r="22" fill="#ffd166" />
        <circle r="10" fill="#07151f" />
      </g>
      <g className="map-marker map-marker--destination" transform="translate(665 228)">
        <circle r="24" fill="#18c6d8" />
        <path
          d="M-7 -1 L-1 7 L10 -9"
          fill="none"
          stroke="#07151f"
          strokeWidth="5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </g>
    </>
  );
}

function GateLabels() {
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

export function StadiumMap({ origin, destination, hasResult }: StadiumMapProps) {
  return (
    <aside className="stadium-card" aria-label="Keyless stadium wayfinding visualization">
      <div className="stadium-card__header">
        <div>
          <p className="result-kicker">Live wayfinding preview</p>
          <h3>VenueFlow Map</h3>
        </div>
        <span className={hasResult ? 'status-chip status-chip--active' : 'status-chip'}>
          {hasResult ? 'Route generated' : 'Preview mode'}
        </span>
      </div>

      <div className="stadium-map-shell">
        <svg
          className="stadium-map"
          viewBox="0 0 760 520"
          role="img"
          aria-labelledby="stadium-title stadium-desc"
        >
          <title id="stadium-title">Stylized stadium map with accessible route</title>
          <desc id="stadium-desc">
            A keyless stadium floorplan showing gates, crowd zones, pitch, sections, and a
            highlighted accessible route from origin to destination.
          </desc>

          <defs>
            <linearGradient id="pitchGradient" x1="0" x2="1" y1="0" y2="1">
              <stop offset="0%" stopColor="#32d583" />
              <stop offset="100%" stopColor="#087443" />
            </linearGradient>
            <linearGradient id="routeGradient" x1="0" x2="1">
              <stop offset="0%" stopColor="#ffd166" />
              <stop offset="50%" stopColor="#18c6d8" />
              <stop offset="100%" stopColor="#1769ff" />
            </linearGradient>
            <filter id="routeGlow" x="-20%" y="-20%" width="140%" height="140%">
              <feGaussianBlur stdDeviation="5" result="blur" />
              <feMerge>
                <feMergeNode in="blur" />
                <feMergeNode in="SourceGraphic" />
              </feMerge>
            </filter>
          </defs>

          <StadiumShell />
          <Pitch />
          <CrowdBands />
          <AccessibleRoute hasResult={hasResult} />
          <MapMarkers />
          <GateLabels />
        </svg>
      </div>

      <div className="route-summary-strip">
        <div>
          <span>From</span>
          <strong>{shortLabel(origin)}</strong>
        </div>
        <div className="route-arrow">→</div>
        <div>
          <span>To</span>
          <strong>{shortLabel(destination)}</strong>
        </div>
      </div>

      <div className="map-legend" aria-label="Map legend">
        <span><i className="legend-dot legend-dot--route" /> Accessible route</span>
        <span><i className="legend-dot legend-dot--crowd" /> Crowd pressure</span>
        <span><i className="legend-dot legend-dot--transit" /> Transit plaza</span>
      </div>
    </aside>
  );
}

import { AccessibleRoute } from './AccessibleRoute';
import { CrowdBands } from './CrowdBands';
import { GateLabels } from './GateLabels';
import { MapMarkers } from './MapMarkers';
import { Pitch } from './Pitch';
import { StadiumShell } from './StadiumShell';

type StadiumMapProps = {
  origin: string;
  destination: string;
  hasResult: boolean;
};

function shortLabel(value: string) {
  return value.trim() || 'Select point';
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

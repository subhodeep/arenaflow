export function MapMarkers() {
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

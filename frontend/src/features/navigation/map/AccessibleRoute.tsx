export function AccessibleRoute({ hasResult }: { hasResult: boolean }) {
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

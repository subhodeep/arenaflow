import { useState } from 'react';
import { NavLink, Route, Routes } from 'react-router-dom';
import { Accessibility } from './features/accessibility/Accessibility';
import { Assistant } from './features/assistant/Assistant';
import { Navigation } from './features/navigation/Navigation';
import { Operations } from './features/operations/Operations';
import { Sustainability } from './features/sustainability/Sustainability';
import { Transportation } from './features/transportation/Transportation';
import { getStrings } from './i18n/strings';
import { getRuntimeConfig } from './services/runtimeConfig';

export default function App() {
  const config = getRuntimeConfig();
  const [language, setLanguage] = useState(config.ARENAFLOW_DEFAULT_LOCALE);
  const [venueId, setVenueId] = useState(config.ARENAFLOW_DEFAULT_VENUE_ID);
  const t = getStrings(language);

  return (
    <div className="app-shell">
      <header className="hero">
        <div>
          <p className="eyebrow">FIFA World Cup 2026 operations</p>
          <h1>{t.title}</h1>
          <p>{t.subtitle}</p>
          <p className="safety-note">{t.safety}</p>
        </div>
        <div className="hero-controls">
          <label className="language-picker">
            Language
            <select value={language} onChange={(event) => setLanguage(event.target.value)}>
              {config.ARENAFLOW_SUPPORTED_LOCALES.map((locale) => (
                <option key={locale} value={locale}>{locale.toUpperCase()}</option>
              ))}
            </select>
          </label>
          <label className="language-picker">
            Venue ID
            <input value={venueId} onChange={(event) => setVenueId(event.target.value)} placeholder="Set ARENAFLOW_DEFAULT_VENUE_ID" required />
          </label>
        </div>
      </header>

      <nav className="tabs" aria-label="ArenaFlow features">
        <NavLink to="/">{t.assistant}</NavLink>
        <NavLink to="/navigation">{t.navigation}</NavLink>
        <NavLink to="/accessibility">{t.accessibility}</NavLink>
        <NavLink to="/transportation">{t.transportation}</NavLink>
        <NavLink to="/sustainability">{t.sustainability}</NavLink>
        <NavLink to="/operations">{t.operations}</NavLink>
      </nav>

      <main>
        <Routes>
          <Route path="/" element={<Assistant language={language} venueId={venueId} />} />
          <Route path="/navigation" element={<Navigation language={language} venueId={venueId} />} />
          <Route path="/accessibility" element={<Accessibility language={language} venueId={venueId} />} />
          <Route path="/transportation" element={<Transportation language={language} venueId={venueId} />} />
          <Route path="/sustainability" element={<Sustainability language={language} venueId={venueId} />} />
          <Route path="/operations" element={<Operations language={language} venueId={venueId} />} />
        </Routes>
      </main>
    </div>
  );
}

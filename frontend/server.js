import compression from 'compression';
import express from 'express';
import helmet from 'helmet';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);
const app = express();
const port = process.env.PORT || 8080;

app.disable('x-powered-by');
app.use(compression());
app.use(
  helmet({
    contentSecurityPolicy: {
      useDefaults: true,
      directives: {
        "default-src": ["'self'"],
        "script-src": ["'self'", "'unsafe-inline'", "https://maps.googleapis.com"],
        "connect-src": ["'self'", process.env.ARENAFLOW_API_BASE_URL || '', "https://maps.googleapis.com"].filter(Boolean),
        "img-src": ["'self'", "data:", "https://*.googleapis.com", "https://*.gstatic.com"],
        "style-src": ["'self'", "'unsafe-inline'", "https://fonts.googleapis.com"],
        "font-src": ["'self'", "https://fonts.gstatic.com"],
        "frame-ancestors": ["'none'"]
      }
    },
    crossOriginEmbedderPolicy: false
  })
);

app.get('/config.js', (req, res) => {
  const config = {
    ARENAFLOW_API_BASE_URL: process.env.ARENAFLOW_API_BASE_URL || 'http://localhost:8000',
    ARENAFLOW_MAPS_BROWSER_API_KEY: process.env.ARENAFLOW_MAPS_BROWSER_API_KEY || '',
    ARENAFLOW_DEFAULT_LOCALE: process.env.ARENAFLOW_DEFAULT_LOCALE || 'en',
    ARENAFLOW_SUPPORTED_LOCALES: (process.env.ARENAFLOW_SUPPORTED_LOCALES || 'en,es').split(',').map((item) => item.trim()).filter(Boolean),
    ARENAFLOW_ENVIRONMENT: process.env.ARENAFLOW_ENVIRONMENT || 'local',
    ARENAFLOW_DEFAULT_VENUE_ID: process.env.ARENAFLOW_DEFAULT_VENUE_ID || '',
    ARENAFLOW_DEFAULT_EVENT_ID: process.env.ARENAFLOW_DEFAULT_EVENT_ID || ''
  };
  res.type('application/javascript');
  res.setHeader('Cache-Control', 'no-store');
  res.send(`window.__ARENAFLOW_CONFIG__ = ${JSON.stringify(config)};`);
});

app.use(express.static(path.join(__dirname, 'dist'), { maxAge: '1h', index: false }));

app.get('*', (req, res) => {
  res.sendFile(path.join(__dirname, 'dist', 'index.html'));
});

app.listen(port, () => {
  console.log(`ArenaFlow frontend listening on ${port}`);
});

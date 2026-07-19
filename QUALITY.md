# ArenaFlow quality gates

ArenaFlow's final hackathon scope prioritizes maintainable, typed, modular code without changing the product behavior that already scores highly for security, efficiency, accessibility, and problem alignment.

## External best-practice references

- FastAPI larger application structure: https://fastapi.tiangolo.com/tutorial/bigger-applications/
- Ruff linter configuration: https://docs.astral.sh/ruff/linter/
- React component decomposition: https://react.dev/learn/thinking-in-react
- Testing Library principles: https://testing-library.com/docs/guiding-principles/
- TypeScript ESLint setup: https://typescript-eslint.io/getting-started/
- Vitest setup: https://vitest.dev/guide/
- Pydantic model design: https://docs.pydantic.dev/latest/concepts/models/

## Backend quality design

- FastAPI route modules stay small and are composed with shared router helpers.
- Gemini orchestration is split by responsibility:
  - client access
  - prompt construction
  - fallback responses
  - payload normalization
  - public service orchestration
- Grounding data uses typed Pydantic models at service boundaries and serializes only when external JSON is needed.
- Repository protocols document service dependencies without coupling business logic to Google Cloud clients.
- Ruff enforces import ordering, correctness, modernization, bugbear, and simplification checks.
- Backend tests are split by topic for easier maintenance and clearer ownership.

## Frontend quality design

- Feature components keep only feature-specific input state.
- Shared request/result/error behavior lives in `useApiMutation`.
- API response contracts are represented in `src/types/api.ts`.
- Result rendering is split into focused components under `src/components/result-card`.
- The stadium SVG is split into map primitives under `src/features/navigation/map`.
- ESLint and TypeScript ESLint provide a frontend quality gate.

## Verification commands

Backend:

```bash
python -m ruff format backend
python -m ruff check backend
python -m pytest backend/tests
```

Frontend, from `frontend/` after Node.js 20/npm are installed:

```bash
npm install
npm run quality
```

Equivalent frontend steps:

```bash
npm run lint
npm run test:run
npm run build
```

## Non-goals for this final scope

- No authentication or authorization behavior changes.
- No new public endpoints.
- No extra runtime network calls.
- No raw HTML rendering.
- No UI accessibility regressions.
- No expansion beyond the ArenaFlow FIFA World Cup 2026 operations/fan-experience problem statement.

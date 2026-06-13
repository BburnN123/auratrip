# Auratrip

Auratrip is an AI-powered trip planner that turns a destination and dates into a dynamic, evidence-based itinerary. It scrapes real-time social-media signals, validates them with specialized agents, and generates itinerary visuals — all orchestrated inside Daytona sandboxes.

## Tech Stack

- **Backend:** Python 3.12, FastAPI, Pydantic
- **Agent Runtime:** Daytona Sandboxes
- **CI/CD:** GitHub Actions
- **Shared Types:** TypeScript interfaces (used by the frontend teammate)

## Project Structure

```
backend/
  src/
    api/main.py              # FastAPI entry point
    agents/                  # Scout, Weather, Planner, Visual agents (stubs)
    client/                  # External API client wrappers (stubs)
    models/                  # Pydantic models
    services/                # Business services (stubs)
  tests/test_main.py         # API unit tests
  requirements.txt           # Python dependencies
  Dockerfile                 # Optional Docker fallback

common/
  types/                     # Shared TypeScript types
  utils/                     # Shared validators/formatters

scripts/
  deploy_daytona.py          # Daytona SDK deployment script
  deploy.sh                  # CI wrapper for deploy_daytona.py

docs/
  ARCHITECTURE.md            # Full architecture and roadmap
```

## Local Development

1. **Install dependencies**

   ```bash
   cd backend
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configure secrets**

   Copy `.env.example` to `.env` and fill in the API keys you need for your current work.

   ```bash
   cp .env.example .env
   ```

3. **Run the API**

   ```bash
   cd backend
   uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
   ```

4. **Run tests**

   ```bash
   cd backend
   pytest tests
   ```

## Deploy to Daytona

Pushing to `main` triggers the `.github/workflows/deploy.yml` GitHub Action. It uses the Daytona SDK to:

1. Build a sandbox image from `backend/requirements.txt`.
2. Clone the repo into the sandbox.
3. Start the FastAPI server.
4. Health-check the public preview URL.

Required repository secrets:

- `DAYTONA_API_KEY`
- `SECRET_KEY`
- `KIMI_API_KEY`
- `TOKENROUTER_API_KEY`
- `BRIGHT_DATA_API_KEY`
- `NOSANA_API_KEY`
- `SENSENOVA_API_KEY`
- `TERMINAL3_API_KEY`
- `VIDEODB_API_KEY`

After deployment, the GitHub Actions log prints the public preview URL:

```
Preview URL: https://8000-<sandbox-id>.<daytona-proxy-domain>
```

Ping it with:

```bash
curl https://8000-<sandbox-id>.<daytona-proxy-domain>/health
```

## Environment Variables

See `.env.example` for the full list of configuration values. Only the variables you actually use need to be set for local development.

## Notes

- PostgreSQL, Redis, and OpenWeather integration are described in `ARCHITECTURE.md` but are **not yet implemented** in the codebase.
- The agent, client, and service modules are placeholder stubs ready for implementation.

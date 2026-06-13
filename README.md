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
  deploy_service.py          # Generic blue-green Daytona deployment
  deploy_daytona.py          # API service wrapper for deploy_service.py
  deploy.sh                  # CI wrapper

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

Pushing to `main` triggers the `.github/workflows/deploy.yml` GitHub Action. It uses the Daytona SDK for a **blue-green** deployment:

1. Build a new sandbox image from `backend/requirements.txt`.
2. Clone the repo into the new sandbox.
3. Start the FastAPI server and run a health check.
4. Only after the health check passes, delete the old `auratrip-api` sandbox(es).

Sandboxes are named `auratrip-api-<timestamp>` and labeled `service=auratrip-api`, so each service has its own namespace and old instances are cleaned up automatically.

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

### Deploying Additional Services

`scripts/deploy_service.py` is generic. Create a new wrapper script (e.g. `scripts/deploy_worker.py`) that sets:

- `DAYTONA_SERVICE_NAME`
- `DAYTONA_SERVICE_PORT`
- `DAYTONA_SERVICE_DIR`
- `DAYTONA_REQUIREMENTS_PATH`
- `DAYTONA_START_COMMAND` (optional)
- `DAYTONA_ENV_KEYS`

Each service is labeled independently, so deployments don't interfere with each other.

## Environment Variables

See `.env.example` for the full list of configuration values. Only the variables you actually use need to be set for local development.

## Notes

- PostgreSQL, Redis, and OpenWeather integration are described in `ARCHITECTURE.md` but are **not yet implemented** in the codebase.
- The agent, client, and service modules are placeholder stubs ready for implementation.

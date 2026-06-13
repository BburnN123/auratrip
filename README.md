# Auratrip1

This project was generated using [Angular CLI](https://github.com/angular/angular-cli) version 22.0.1.

## Development server

To start a local development server, run:

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

Once the server is running, open your browser and navigate to `http://localhost:4200/`. The application will automatically reload whenever you modify any of the source files.

## Code scaffolding

Angular CLI includes powerful code scaffolding tools. To generate a new component, run:

```bash
ng generate component component-name
```

For a complete list of available schematics (such as `components`, `directives`, or `pipes`), run:

```bash
ng generate --help
```

## Building

Pushing to `main` triggers the `.github/workflows/deploy.yml` GitHub Action. It uses the Daytona SDK for a **blue-green** deployment:

1. Build a new sandbox image from `backend/requirements.txt`.
2. Clone the repo into the new sandbox.
3. Start the FastAPI server and run a health check.
4. Only after the health check passes, delete the old `auratrip-api` sandbox(es).

Sandboxes are named `auratrip-api-<timestamp>` and labeled `service=auratrip-api`, so each service has its own namespace and old instances are cleaned up automatically.

This will compile your project and store the build artifacts in the `dist/` directory. By default, the production build optimizes your application for performance and speed.

## Running unit tests

To execute unit tests with the [Vitest](https://vitest.dev/) test runner, use the following command:

```bash
ng test
```

## Running end-to-end tests

For end-to-end (e2e) testing, run:

```bash
ng e2e
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

## Additional Resources

For more information on using the Angular CLI, including detailed command references, visit the [Angular CLI Overview and Command Reference](https://angular.dev/tools/cli) page.

"""Deploy the Auratrip backend to a Daytona Sandbox using the declarative builder.

This does NOT require a Dockerfile. Daytona builds the sandbox image from
backend/requirements.txt, clones the repo into the sandbox, and starts uvicorn.
"""

import os
import time

from daytona import (
    CreateSandboxFromImageParams,
    Daytona,
    DaytonaConfig,
    Image,
    Resources,
    SessionExecuteRequest,
)

# Secrets that should be forwarded into the sandbox environment.
ENV_KEYS = [
    "SECRET_KEY",
    "KIMI_API_KEY",
    "TOKENROUTER_API_KEY",
    "BRIGHT_DATA_API_KEY",
    "NOSANA_API_KEY",
    "SENSENOVA_API_KEY",
    "TERMINAL3_API_KEY",
    "VIDEODB_API_KEY",
]


def get_env_vars() -> dict[str, str]:
    return {k: os.environ[k] for k in ENV_KEYS if k in os.environ}


def main() -> None:
    api_key = os.environ["DAYTONA_API_KEY"]
    config = DaytonaConfig(api_key=api_key)
    daytona = Daytona(config)

    repo = os.environ.get("GITHUB_REPOSITORY", "owner/repo")
    ref = os.environ.get("GITHUB_SHA", "main")
    github_token = os.environ.get("GITHUB_TOKEN")

    # Build a declarative image with Python 3.12 + our dependencies.
    image = (
        Image.debian_slim("3.12")
        .run_commands(
            "apt-get update && apt-get install -y --no-install-recommends git "
            "&& rm -rf /var/lib/apt/lists/*"
        )
        .pip_install_from_requirements("backend/requirements.txt")
        .workdir("/home/daytona/app")
    )

    params = CreateSandboxFromImageParams(
        image=image,
        env_vars=get_env_vars(),
        resources=Resources(cpu=1, memory=2, disk=8),
        auto_stop_interval=0,  # Keep the API sandbox running.
    )

    print("Building Daytona sandbox image (this may take a minute)...")
    sandbox = daytona.create(params, timeout=0, on_snapshot_create_logs=print)
    print(f"Sandbox created: {sandbox.id}")

    # Clone the repository into the sandbox.
    if github_token:
        clone_url = f"https://x-access-token:{github_token}@github.com/{repo}.git"
    else:
        clone_url = f"https://github.com/{repo}.git"

    clone_cmd = (
        f"git clone --depth 1 {clone_url} /home/daytona/app "
        f"&& cd /home/daytona/app && git fetch --depth 1 origin {ref} "
        f"&& git checkout {ref}"
    )
    print("Cloning repository into sandbox...")
    result = sandbox.process.exec(clone_cmd)
    print(result.result)

    # Start uvicorn in a persistent session so it outlives this script.
    session_id = "auratrip-api"
    sandbox.process.create_session(session_id)
    command = sandbox.process.execute_session_command(
        session_id,
        SessionExecuteRequest(
            command=(
                "cd /home/daytona/app/backend && "
                "nohup uvicorn src.api.main:app --host 0.0.0.0 --port 8000 "
                "> /tmp/uvicorn.log 2>&1 &"
            ),
            run_async=True,
        ),
    )
    print(f"Uvicorn started: cmd_id={command.cmd_id}")

    # Give the server a moment to start, then health-check internally.
    time.sleep(5)
    health = sandbox.process.exec(
        "curl -s http://localhost:8000/health || echo 'not ready'"
    )
    print("Health check:", health.result)

    # Expose the service via a Daytona preview URL.
    preview = sandbox.get_preview_link(8000)
    print(f"Preview URL: {preview.url}")
    print(f"Preview Token: {preview.token}")


if __name__ == "__main__":
    main()

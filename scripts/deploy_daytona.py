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


def exec_or_raise(sandbox, command: str) -> str:
    """Execute a command in the sandbox and raise on non-zero exit codes."""
    result = sandbox.process.exec(command)
    if result.exit_code != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.exit_code}: {command}\n{result.result}"
        )
    return result.result


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
        auto_stop_interval=60,  # Keep the sandbox alive for 60 minutes of inactivity.
        public=True,  # Preview URL is reachable without an auth token.
    )

    print("Building Daytona sandbox image (this may take a minute)...")
    sandbox = daytona.create(params, timeout=0, on_snapshot_create_logs=print)
    print(f"Sandbox created: {sandbox.id}")

    # Clone the repository into the sandbox.
    if github_token:
        clone_url = f"https://x-access-token:{github_token}@github.com/{repo}.git"
    else:
        clone_url = f"https://github.com/{repo}.git"

    print("Cloning repository into sandbox...")
    exec_or_raise(sandbox, f"git clone {clone_url} /home/daytona/app")
    exec_or_raise(sandbox, f"cd /home/daytona/app && git checkout {ref}")
    print("Repository cloned and checked out.")

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

    health_check_script = (
        "import urllib.request; "
        "resp = urllib.request.urlopen('http://localhost:8000/health', timeout=5); "
        "print(resp.read().decode())"
    )
    try:
        health = exec_or_raise(
            sandbox, f"python -c '{health_check_script}'"
        )
        print("Health check:", health)
    except RuntimeError as exc:
        print("Health check failed.")
        print(exc)
        print("Uvicorn logs:")
        logs = sandbox.process.exec("cat /tmp/uvicorn.log || echo 'no logs'")
        print(logs.result)
        raise

    # Expose the service via a Daytona preview URL.
    preview = sandbox.get_preview_link(8000)
    print(f"Preview URL: {preview.url}")
    print(f"Preview Token: {preview.token}")


if __name__ == "__main__":
    main()

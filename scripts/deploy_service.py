"""Generic blue-green deployment of a service to a Daytona Sandbox.

Environment variables used:
  DAYTONA_SERVICE_NAME      Name of the service (default: auratrip-api)
  DAYTONA_SERVICE_PORT      Port the service listens on (default: 8000)
  DAYTONA_SERVICE_DIR       Directory inside the repo to run from (default: backend)
  DAYTONA_REQUIREMENTS_PATH Path to requirements.txt (default: backend/requirements.txt)
  DAYTONA_START_COMMAND     Command used to start the service
  DAYTONA_ENV_KEYS          Comma-separated list of env vars to forward

Always required:
  DAYTONA_API_KEY
  GITHUB_REPOSITORY
  GITHUB_SHA
  GITHUB_TOKEN (optional, for private repos)
"""

import os
import time
import urllib.request

from daytona import (
    CreateSandboxFromImageParams,
    Daytona,
    DaytonaConfig,
    Image,
    ListSandboxesQuery,
    Resources,
    SessionExecuteRequest,
)


def get_env_vars(keys: list[str]) -> dict[str, str]:
    return {k.strip(): os.environ[k.strip()] for k in keys if k.strip() in os.environ}


def exec_or_raise(sandbox, command: str) -> str:
    result = sandbox.process.exec(command)
    if result.exit_code != 0:
        raise RuntimeError(
            f"Command failed with exit code {result.exit_code}: {command}\n{result.result}"
        )
    return result.result


def find_old_sandboxes(daytona: Daytona, service_name: str) -> list:
    query = ListSandboxesQuery(labels={"service": service_name})
    return list(daytona.list(query))


def health_check(preview_url: str, token: str | None) -> str:
    req = urllib.request.Request(
        preview_url + "/health",
        headers={"x-daytona-preview-token": token} if token else {},
    )
    with urllib.request.urlopen(req, timeout=10) as resp:
        return resp.read().decode()


def deploy_service(
    service_name: str,
    service_port: int,
    service_dir: str,
    requirements_path: str,
    start_command: str,
    env_keys: list[str],
) -> str:
    api_key = os.environ["DAYTONA_API_KEY"]
    config = DaytonaConfig(api_key=api_key)
    daytona = Daytona(config)

    repo = os.environ.get("GITHUB_REPOSITORY", "owner/repo")
    ref = os.environ.get("GITHUB_SHA", "main")
    github_token = os.environ.get("GITHUB_TOKEN")

    old_sandboxes = find_old_sandboxes(daytona, service_name)
    print(f"Found {len(old_sandboxes)} existing sandbox(s) for service '{service_name}'")

    new_name = f"{service_name}-{int(time.time())}"
    image = (
        Image.debian_slim("3.12")
        .run_commands(
            "apt-get update && apt-get install -y --no-install-recommends git "
            "&& rm -rf /var/lib/apt/lists/*"
        )
        .pip_install_from_requirements(requirements_path)
        .workdir("/home/daytona/app")
    )

    params = CreateSandboxFromImageParams(
        name=new_name,
        image=image,
        labels={"service": service_name},
        env_vars=get_env_vars(env_keys),
        resources=Resources(cpu=1, memory=2, disk=8),
        auto_stop_interval=60,
        public=True,
    )

    print(f"Building new sandbox '{new_name}'...")
    new_sandbox = daytona.create(params, timeout=0, on_snapshot_create_logs=print)
    print(f"Sandbox created: {new_sandbox.id}")

    try:
        if github_token:
            clone_url = f"https://x-access-token:{github_token}@github.com/{repo}.git"
        else:
            clone_url = f"https://github.com/{repo}.git"

        print("Cloning repository into sandbox...")
        exec_or_raise(new_sandbox, f"git clone {clone_url} /home/daytona/app")
        exec_or_raise(new_sandbox, f"cd /home/daytona/app && git checkout {ref}")
        print("Repository cloned and checked out.")

        session_id = f"{service_name}-session"
        new_sandbox.process.create_session(session_id)
        command = new_sandbox.process.execute_session_command(
            session_id,
            SessionExecuteRequest(
                command=start_command,
                run_async=True,
            ),
        )
        print(f"Service started: cmd_id={command.cmd_id}")

        time.sleep(5)
        preview = new_sandbox.get_preview_link(service_port)
        print(f"Preview URL: {preview.url}")
        print(f"Preview Token: {preview.token}")

        body = health_check(preview.url, preview.token)
        print("Health check:", body)
        if '"status":"ok"' not in body and '"status": "ok"' not in body:
            raise RuntimeError(f"Unexpected health response: {body}")

    except Exception as exc:
        print("Deployment failed. New sandbox will be removed.")
        print(exc)
        print("Uvicorn logs:")
        logs = new_sandbox.process.exec("cat /tmp/uvicorn.log || echo 'no logs'")
        print(logs.result)
        daytona.delete(new_sandbox)
        raise

    # Blue-green cutover: new sandbox is healthy, remove old ones.
    for old in old_sandboxes:
        if old.id == new_sandbox.id:
            continue
        print(f"Deleting old sandbox: {old.id} ({old.name})")
        try:
            daytona.delete(old)
        except Exception as exc:
            print(f"Warning: failed to delete old sandbox {old.id}: {exc}")

    print(f"\nService '{service_name}' deployed successfully.")
    print(f"Preview URL: {preview.url}")
    return preview.url


def main() -> None:
    service_name = os.environ.get("DAYTONA_SERVICE_NAME", "auratrip-api")
    service_port = int(os.environ.get("DAYTONA_SERVICE_PORT", "8000"))
    service_dir = os.environ.get("DAYTONA_SERVICE_DIR", "backend")
    requirements_path = os.environ.get(
        "DAYTONA_REQUIREMENTS_PATH", "backend/requirements.txt"
    )
    default_start = (
        f"cd /home/daytona/app/{service_dir} && "
        f"nohup uvicorn src.api.main:app --host 0.0.0.0 --port {service_port} "
        "> /tmp/uvicorn.log 2>&1 &"
    )
    start_command = os.environ.get("DAYTONA_START_COMMAND", default_start)
    env_keys = os.environ.get("DAYTONA_ENV_KEYS", "").split(",")
    env_keys = [k.strip() for k in env_keys if k.strip()]

    deploy_service(
        service_name=service_name,
        service_port=service_port,
        service_dir=service_dir,
        requirements_path=requirements_path,
        start_command=start_command,
        env_keys=env_keys,
    )


if __name__ == "__main__":
    main()

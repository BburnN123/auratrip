"""Deploy the Auratrip API service to Daytona using blue-green cutover."""

import os

import deploy_service


def main() -> None:
    os.environ.setdefault("DAYTONA_SERVICE_NAME", "auratrip-api")
    os.environ.setdefault("DAYTONA_SERVICE_PORT", "8000")
    os.environ.setdefault("DAYTONA_SERVICE_DIR", "backend")
    os.environ.setdefault("DAYTONA_REQUIREMENTS_PATH", "backend/requirements.txt")

    env_keys = [
        "SECRET_KEY",
        "KIMI_API_KEY",
        "TOKENROUTER_API_KEY",
        "BRIGHT_DATA_API_KEY",
        "NOSANA_API_KEY",
        "SENSENOVA_API_KEY",
        "TERMINAL3_API_KEY",
        "VIDEODB_API_KEY",
    ]
    os.environ["DAYTONA_ENV_KEYS"] = ",".join(env_keys)

    deploy_service.main()


if __name__ == "__main__":
    main()

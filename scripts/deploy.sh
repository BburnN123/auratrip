#!/usr/bin/env bash
set -euo pipefail

# Deploy the Auratrip backend to Daytona using the Daytona SDK declarative builder.
# Docker is NOT required for this path; Daytona builds the image from requirements.txt.

python scripts/deploy_daytona.py

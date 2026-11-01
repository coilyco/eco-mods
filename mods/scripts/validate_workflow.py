#!/usr/bin/env python3
"""Parse the CI workflow so syntax fails before dispatch."""

from pathlib import Path

import yaml


yaml.safe_load(Path(".github/workflows/ci.yml").read_text(encoding="utf-8"))

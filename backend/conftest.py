"""Pytest bootstrap: provide safe settings before Django settings load."""

import os

os.environ.setdefault("DEBUG", "true")
os.environ.setdefault("SECRET_KEY", "test-only-secret-key")

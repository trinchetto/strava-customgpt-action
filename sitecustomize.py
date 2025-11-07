"""
Project-wide sitecustomize hook.

Ensures pytest does not auto-load unrelated third-party plugins from the host
environment, preventing import errors when running the test suite.
"""

from __future__ import annotations

import os

os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")

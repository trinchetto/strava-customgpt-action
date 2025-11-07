"""
Testing utilities and entry points for the project.
"""

from __future__ import annotations

import os
from collections.abc import Sequence

import pytest


def pytest_main(args: Sequence[str] | None = None) -> int:
    """
    Wrapper around pytest's console entry point that disables auto-loading
    of unrelated plugins living in the global environment.
    """

    os.environ.setdefault("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    if args is None:
        return pytest.main()
    return pytest.main(list(args))


def main() -> None:
    raise SystemExit(pytest_main())

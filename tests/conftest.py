"""Test configuration for pytest.

Ensure the project's `src/` directory is on sys.path so tests can import
the `companies_simulator` package when running from the repository root.
"""
import sys
from pathlib import Path


# Insert src/ at front of sys.path so imports like
# `from companies_simulator...` work when running tests from repo root
ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

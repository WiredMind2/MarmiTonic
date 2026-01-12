"""
Pytest configuration and shared fixtures for all tests.
"""

import pytest
import sys
import os
from pathlib import Path

# Add backend directory to path for imports
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))


@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture that returns the test data directory path"""
    return Path(__file__).parent / "test_data"


@pytest.fixture(autouse=True)
def reset_singletons():
    """Reset any singleton instances between tests"""
    yield
    # Add cleanup code here if needed

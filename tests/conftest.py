"""Test configuration and fixtures."""

import os
import sys
from pathlib import Path
from unittest.mock import patch

import pytest


# Add src to Python path for imports
src_path = Path(__file__).parent.parent / "src"
if str(src_path) not in sys.path:
    sys.path.insert(0, str(src_path))


@pytest.fixture(autouse=True)
def block_network_calls():
    """Automatically block all network calls during tests to prevent accidental API usage."""
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_client = mock_anthropic.return_value
        mock_client.messages.create.side_effect = Exception(
            "Real API calls are blocked in tests! Use proper mocking."
        )
        yield mock_client


@pytest.fixture(autouse=True)
def ensure_test_env():
    """Ensure we're in a test environment with safe API key."""
    original_key = os.environ.get("ANTHROPIC_API_KEY")
    os.environ["ANTHROPIC_API_KEY"] = "test-key-safe-for-testing"
    yield
    if original_key is not None:
        os.environ["ANTHROPIC_API_KEY"] = original_key
    else:
        os.environ.pop("ANTHROPIC_API_KEY", None)


@pytest.fixture
def mock_anthropic_client():
    """Provide a properly mocked Anthropic client for tests that need it."""
    with patch("anthropic.Anthropic") as mock_anthropic:
        mock_client = mock_anthropic.return_value
        yield mock_client

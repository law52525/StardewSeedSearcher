"""
Pytest configuration and fixtures
Pytest配置和fixtures
"""

import pytest
import asyncio
import requests
import time
from typing import Dict, Any, List
from internal.features import WeatherPredictor
from internal.models import WeatherCondition, Season, SearchRequest


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def server_url():
    """Get server URL for testing."""
    return "http://localhost:5000"


@pytest.fixture
def server_health_check(server_url):
    """Check if server is running and healthy."""
    try:
        response = requests.get(f"{server_url}/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("status") == "ok"
        return False
    except Exception as e:
        return False


@pytest.fixture
def weather_predictor():
    """Create a fresh WeatherPredictor instance for each test."""
    predictor = WeatherPredictor()
    predictor.set_enabled(True)
    return predictor


@pytest.fixture
def spring_condition():
    """Create a Spring weather condition for testing."""
    return WeatherCondition(
        season=Season.SPRING,
        start_day=1,
        end_day=10,
        min_rain_days=5
    )


@pytest.fixture
def summer_condition():
    """Create a Summer weather condition for testing."""
    return WeatherCondition(
        season=Season.SUMMER,
        start_day=1,
        end_day=10,
        min_rain_days=5
    )


@pytest.fixture
def fall_condition():
    """Create a Fall weather condition for testing."""
    return WeatherCondition(
        season=Season.FALL,
        start_day=1,
        end_day=10,
        min_rain_days=5
    )


# Removed test_weather_conditions as it was for test sample 3 which is excluded


@pytest.fixture
def sample_search_request():
    """Create a sample search request for testing."""
    return SearchRequest(
        startSeed=0,
        endSeed=1000,
        useLegacyRandom=False,
        weatherConditions=[
            WeatherCondition(
                season=Season.SPRING,
                startDay=1,
                endDay=10,
                minRainDays=5
            )
        ],
        outputLimit=100
    )


@pytest.fixture
def expected_seeds_sample1():
    """Expected seeds for sample 1 test case."""
    return [59, 73, 101, 142, 659, 932, 938]


# Removed expected_seeds_sample3 as it's not needed (test sample 3 is excluded)


@pytest.fixture
def invalid_weather_conditions():
    """Invalid weather conditions for validation testing."""
    # These will be created in the test functions to avoid validation errors during fixture setup
    return [
        # minRainDays equals day range
        {
            "season": Season.SPRING,
            "start_day": 1,
            "end_day": 10,
            "min_rain_days": 10
        },
        # minRainDays greater than day range
        {
            "season": Season.SPRING,
            "start_day": 1,
            "end_day": 10,
            "min_rain_days": 15
        }
    ]


@pytest.fixture
def websocket_message_samples():
    """Sample WebSocket messages for testing."""
    return {
        "start": {
            "type": "start",
            "total": 1000
        },
        "progress": {
            "type": "progress",
            "checkedCount": 100,
            "total": 1000,
            "progress": 10.0,
            "speed": 50.0,
            "elapsed": 2.0
        },
        "found": {
            "type": "found",
            "seed": 12345
        },
        "complete": {
            "type": "complete",
            "totalFound": 5,
            "elapsed": 10.5
        }
    }


@pytest.fixture
def test_seed_ranges():
    """Different seed ranges for testing (max 100k)."""
    return {
        "small": (0, 1000),
        "medium": (0, 100000),
        "large": (0, 100000)  # Reduced from 1M to 100k
    }


@pytest.fixture
def benchmark_seeds():
    """Seeds for performance benchmarking (reduced range)."""
    return list(range(0, 10000, 100))  # Every 100th seed from 0 to 10000


# Pytest hooks
def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that don't require external dependencies"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that require server running"
    )
    config.addinivalue_line(
        "markers", "slow: Slow running tests"
    )
    config.addinivalue_line(
        "markers", "api: API endpoint tests"
    )
    config.addinivalue_line(
        "markers", "weather: Weather predictor tests"
    )
    config.addinivalue_line(
        "markers", "validation: Data validation tests"
    )
    config.addinivalue_line(
        "markers", "websocket: WebSocket message tests"
    )
    config.addinivalue_line(
        "markers", "consistency: Consistency tests with Go version"
    )
    config.addinivalue_line(
        "markers", "benchmark: Performance benchmark tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names."""
    for item in items:
        # Add markers based on test file names
        if "test_weather" in item.nodeid:
            item.add_marker(pytest.mark.weather)
        elif "test_api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        elif "test_validation" in item.nodeid:
            item.add_marker(pytest.mark.validation)
        elif "test_websocket" in item.nodeid:
            item.add_marker(pytest.mark.websocket)
        elif "test_consistency" in item.nodeid:
            item.add_marker(pytest.mark.consistency)
        elif "test_benchmark" in item.nodeid:
            item.add_marker(pytest.mark.benchmark)
        
        # Add slow marker for tests that might take time
        if "large" in item.nodeid or "benchmark" in item.nodeid:
            item.add_marker(pytest.mark.slow)


def pytest_runtest_setup(item):
    """Setup for each test run."""
    # Skip integration tests if server is not running
    if "integration" in item.keywords:
        # Check if server is running by making a direct request
        try:
            response = requests.get("http://localhost:5000/api/health", timeout=5)
            if response.status_code != 200:
                pytest.skip(f"Server not running (status: {response.status_code}), skipping integration test")
            data = response.json()
            if data.get("status") != "ok":
                pytest.skip(f"Server not healthy (status: {data.get('status')}), skipping integration test")
        except Exception as e:
            pytest.skip(f"Server not running (error: {str(e)}), skipping integration test")


def pytest_runtest_teardown(item, nextitem):
    """Teardown after each test run."""
    pass


# Custom pytest markers
pytest_plugins = ["pytest_mock"]

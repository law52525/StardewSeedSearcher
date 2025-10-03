"""
Test API endpoints functionality
测试API端点功能
"""

import pytest
import requests
import json
from internal.models import SearchRequest, WeatherCondition, Season


@pytest.mark.api
@pytest.mark.integration
class TestAPIEndpoints:
    """Test API endpoints functionality."""

    def test_health_endpoint(self, server_url):
        """Test health endpoint."""
        response = requests.get(f"{server_url}/api/health")
        assert response.status_code == 200, "Health endpoint should return 200"
        
        data = response.json()
        assert "status" in data, "Health response should contain status"
        assert data["status"] == "ok", "Health status should be 'ok'"

    def test_search_endpoint_valid_request(self, server_url, sample_search_request):
        """Test search endpoint with valid request."""
        
        response = requests.post(
            f"{server_url}/api/search",
            json=sample_search_request.model_dump(by_alias=True),
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, "Valid search request should return 200"
        
        data = response.json()
        assert "message" in data, "Response should contain message"
        assert data["message"] == "Search started.", "Response message should be 'Search started.'"

    def test_search_endpoint_invalid_request_min_rain_days(self, server_url):
        """Test search endpoint with invalid minRainDays request."""
        
        invalid_request = {
            "startSeed": 0,
            "endSeed": 100000,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 10  # Invalid: equals day range
                }
            ],
            "outputLimit": 20
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=invalid_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422, "Invalid request should return 422"
        
        data = response.json()
        assert "detail" in data, "Error response should contain detail"

    def test_search_endpoint_invalid_request_empty_conditions(self, server_url):
        """Test search endpoint with empty weather conditions."""
        
        invalid_request = {
            "startSeed": 0,
            "endSeed": 100000,
            "useLegacyRandom": False,
            "weatherConditions": [],  # Empty list - API accepts this
            "outputLimit": 20
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=invalid_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, "Empty conditions request should return 200"
        data = response.json()
        assert "message" in data, "Response should contain message"

    def test_search_endpoint_invalid_weather_conditions_validation(self, server_url):
        """Test search endpoint with invalid weather conditions that should return 422."""
        
        # Test case 1: min_rain_days equals day range (impossible)
        invalid_request1 = {
            "startSeed": 0,
            "endSeed": 100,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 1,
                    "minRainDays": 1  # 1 rain day in 1 day range = impossible
                }
            ],
            "outputLimit": 20
        }
        
        response1 = requests.post(
            f"{server_url}/api/search",
            json=invalid_request1,
            headers={"Content-Type": "application/json"}
        )
        
        assert response1.status_code == 422, "Invalid min_rain_days should return 422"
        data1 = response1.json()
        assert "detail" in data1, "Error response should contain detail"
        
        # Test case 2: start_day > end_day
        invalid_request2 = {
            "startSeed": 0,
            "endSeed": 100,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 5,
                    "endDay": 3,  # start > end
                    "minRainDays": 1
                }
            ],
            "outputLimit": 20
        }
        
        response2 = requests.post(
            f"{server_url}/api/search",
            json=invalid_request2,
            headers={"Content-Type": "application/json"}
        )
        
        assert response2.status_code == 422, "Invalid day range should return 422"
        data2 = response2.json()
        assert "detail" in data2, "Error response should contain detail"
        
        # Test case 3: min_rain_days > day range
        invalid_request3 = {
            "startSeed": 0,
            "endSeed": 100,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 5,
                    "minRainDays": 6  # 6 rain days in 5 day range = impossible
                }
            ],
            "outputLimit": 20
        }
        
        response3 = requests.post(
            f"{server_url}/api/search",
            json=invalid_request3,
            headers={"Content-Type": "application/json"}
        )
        
        assert response3.status_code == 422, "Invalid min_rain_days range should return 422"
        data3 = response3.json()
        assert "detail" in data3, "Error response should contain detail"

    def test_search_endpoint_invalid_request_negative_seeds(self, server_url):
        """Test search endpoint with negative seed values."""
        
        invalid_request = {
            "startSeed": -1,  # Invalid: negative start seed
            "endSeed": 100000,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 20
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=invalid_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422, "Invalid request should return 422"

    def test_search_endpoint_invalid_request_seed_range(self, server_url):
        """Test search endpoint with invalid seed range."""
        
        invalid_request = {
            "startSeed": 100,  # Invalid: start > end
            "endSeed": 50,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 20
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=invalid_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 500, "Invalid seed range should return 500"

    @pytest.mark.parametrize("start_seed,end_seed,use_legacy_random", [
        (0, 100, False),
        (0, 1000, True),
        (1000, 2000, False),
        (0, 10000, True),
    ])
    def test_search_endpoint_various_parameters(self, server_url, 
                                               start_seed, end_seed, use_legacy_random):
        """Test search endpoint with various parameters."""
        
        request_data = {
            "startSeed": start_seed,
            "endSeed": end_seed,
            "useLegacyRandom": use_legacy_random,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 10
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, f"Request with start={start_seed}, end={end_seed}, legacy={use_legacy_random} should succeed"

    def test_search_endpoint_large_range(self, server_url):
        """Test search endpoint with large seed range."""
        
        request_data = {
            "startSeed": 0,
            "endSeed": 1000000,  # Large range
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 5  # Small output limit
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, "Large range request should be accepted"

    def test_search_endpoint_multiple_weather_conditions(self, server_url):
        """Test search endpoint with multiple weather conditions."""
        
        request_data = {
            "startSeed": 0,
            "endSeed": 10000,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                },
                {
                    "season": "Summer",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                },
                {
                    "season": "Fall",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 10
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=request_data,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200, "Multiple weather conditions request should be accepted"

    def test_search_endpoint_missing_required_fields(self, server_url):
        """Test search endpoint with missing required fields."""
        
        # Missing startSeed
        invalid_request = {
            "endSeed": 100000,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 20
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=invalid_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 422, "Missing required fields should return 422"

    def test_search_endpoint_invalid_content_type(self, server_url):
        """Test search endpoint with invalid content type."""
        
        request_data = {
            "startSeed": 0,
            "endSeed": 100,
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 10
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            data=json.dumps(request_data),  # Missing Content-Type header
            headers={"Content-Type": "text/plain"}
        )
        
        # Should still work as FastAPI can handle JSON in various ways
        assert response.status_code in [200, 422], "Request should be processed"

    def test_search_endpoint_timeout_handling(self, server_url):
        """Test search endpoint timeout handling."""
        
        # Very large range that might timeout
        request_data = {
            "startSeed": 0,
            "endSeed": 10000000,  # Very large range
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 1
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=request_data,
            headers={"Content-Type": "application/json"},
            timeout=5  # Short timeout
        )
        
        # Should accept the request even if it takes time to process
        assert response.status_code == 200, "Large range request should be accepted"

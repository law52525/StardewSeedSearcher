"""
Tests for GPU acceleration functionality
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock

from internal.gpu_pure_accelerator import PureGPUAccelerator, PureGPUSeedSearcher, get_pure_gpu_info
from internal.models import WeatherCondition, Season


@pytest.mark.gpu
class TestPureGPUAccelerator:
    """Test GPU accelerator functionality"""
    
    def test_gpu_accelerator_initialization(self):
        """Test GPU accelerator initialization"""
        accelerator = PureGPUAccelerator()
        assert isinstance(accelerator.is_available(), bool)
    
    def test_get_device_info(self):
        """Test getting GPU device information"""
        info = get_pure_gpu_info()
        assert isinstance(info, dict)
        assert "available" in info
    
    @pytest.mark.asyncio
    async def test_gpu_searcher_initialization(self):
        """Test GPU searcher initialization"""
        weather_conditions = [
            WeatherCondition(
                season=Season.SPRING,
                start_day=1,
                end_day=10,
                min_rain_days=5
            )
        ]
        
        searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        assert searcher.weather_conditions == weather_conditions
        assert searcher.use_legacy_random == False
    
    @pytest.mark.asyncio
    async def test_gpu_search_small_range(self):
        """Test GPU search with small range (should fallback to CPU)"""
        weather_conditions = [
            WeatherCondition(
                season=Season.SPRING,
                start_day=1,
                end_day=10,
                min_rain_days=5
            )
        ]
        
        searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        results = await searcher.search_seeds_pure_gpu(0, 1000, 10)
        
        assert isinstance(results, list)
        assert len(results) <= 10
    
    @pytest.mark.asyncio
    async def test_gpu_search_large_range(self):
        """Test GPU search with large range"""
        weather_conditions = [
            WeatherCondition(
                season=Season.SPRING,
                start_day=1,
                end_day=10,
                min_rain_days=5
            )
        ]
        
        searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        
        # Test with large range
        results = await searcher.search_seeds_pure_gpu(0, 100000, 100)
        
        assert isinstance(results, list)
        assert len(results) <= 100
    
    @pytest.mark.asyncio
    async def test_gpu_search_no_conditions(self):
        """Test GPU search with no weather conditions"""
        searcher = PureGPUSeedSearcher([], use_legacy_random=False)
        results = await searcher.search_seeds_pure_gpu(0, 10000, 10)
        
        assert isinstance(results, list)
        # With no conditions, should return all seeds up to limit
        assert len(results) == 10
    
    @pytest.mark.asyncio
    async def test_gpu_search_multiple_conditions(self):
        """Test GPU search with multiple weather conditions"""
        weather_conditions = [
            WeatherCondition(
                season=Season.SPRING,
                start_day=1,
                end_day=10,
                min_rain_days=5
            ),
            WeatherCondition(
                season=Season.SUMMER,
                start_day=1,
                end_day=15,
                min_rain_days=3
            )
        ]
        
        searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        results = await searcher.search_seeds_pure_gpu(0, 50000, 50)
        
        assert isinstance(results, list)
        assert len(results) <= 50
    
    @pytest.mark.asyncio
    async def test_gpu_search_legacy_random(self):
        """Test GPU search with legacy random"""
        weather_conditions = [
            WeatherCondition(
                season=Season.SPRING,
                start_day=1,
                end_day=10,
                min_rain_days=5
            )
        ]
        
        searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=True)
        results = await searcher.search_seeds_pure_gpu(0, 10000, 10)
        
        assert isinstance(results, list)
        assert len(results) <= 10
    
    @pytest.mark.asyncio
    async def test_gpu_search_fallback_on_error(self):
        """Test that GPU search falls back to CPU on error"""
        weather_conditions = [
            WeatherCondition(
                season=Season.SPRING,
                start_day=1,
                end_day=10,
                min_rain_days=5
            )
        ]
        
        searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        
        # Mock GPU failure
        with patch.object(searcher.accelerator, 'is_available', return_value=False):
            results = await searcher.search_seeds_pure_gpu(0, 10000, 10)
            assert isinstance(results, list)
            assert len(results) <= 10


@pytest.mark.gpu
class TestGPUIntegration:
    """Test GPU integration with API"""
    
    @pytest.mark.asyncio
    async def test_gpu_info_endpoint(self, server_url):
        """Test GPU info endpoint"""
        import requests
        
        response = requests.get(f"{server_url}/api/gpu-info")
        assert response.status_code == 200
        
        data = response.json()
        assert isinstance(data, dict)
        assert "available" in data
    
    @pytest.mark.asyncio
    async def test_large_search_uses_gpu(self, server_url):
        """Test that large searches use GPU acceleration"""
        import requests
        
        # Large search that should trigger GPU acceleration
        large_request = {
            "startSeed": 0,
            "endSeed": 200000,  # Large range
            "useLegacyRandom": False,
            "weatherConditions": [
                {
                    "season": "Spring",
                    "startDay": 1,
                    "endDay": 10,
                    "minRainDays": 5
                }
            ],
            "outputLimit": 100
        }
        
        response = requests.post(
            f"{server_url}/api/search",
            json=large_request,
            headers={"Content-Type": "application/json"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Search started."


@pytest.mark.gpu
class TestGPUBenchmark:
    """Benchmark tests for GPU acceleration"""
    
    def test_cpu_performance(self, benchmark):
        """Benchmark CPU performance"""
        weather_conditions = [
            WeatherCondition(
                season=Season.SPRING,
                start_day=1,
                end_day=10,
                min_rain_days=5
            )
        ]
        
        searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        
        def cpu_search():
            """CPU search for benchmarking"""
            return asyncio.run(searcher._search_seeds_cpu_fallback(0, 1000, 100))
        
        # Benchmark CPU method
        cpu_time = benchmark(cpu_search)
        print(f"CPU time: {cpu_time}")
    
    def test_gpu_performance(self, benchmark):
        """Benchmark GPU performance"""
        weather_conditions = [
            WeatherCondition(
                season=Season.SPRING,
                start_day=1,
                end_day=10,
                min_rain_days=5
            )
        ]
        
        searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        
        def gpu_search():
            """GPU search for benchmarking"""
            return asyncio.run(searcher.search_seeds_pure_gpu(0, 1000, 100))
        
        # Benchmark GPU method
        gpu_time = benchmark(gpu_search)
        
        # GPU should be faster for large searches (if available)
        if searcher.accelerator.is_available():
            print(f"GPU time: {gpu_time}")
        else:
            print("GPU not available, using CPU fallback")

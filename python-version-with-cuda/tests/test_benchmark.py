"""
Performance benchmark tests
性能基准测试
"""

import pytest
import asyncio
from internal.features import WeatherPredictor
from internal.models import WeatherCondition, Season
from internal.core import get_hash_from_string, get_hash_from_array, get_random_seed
from internal.gpu_pure_accelerator import PureGPUSeedSearcher


@pytest.mark.benchmark
@pytest.mark.slow
class TestPerformanceBenchmarks:
    """Test performance benchmarks."""

    def test_hash_from_string_benchmark(self, benchmark, benchmark_seeds):
        """Benchmark hash from string performance."""
        test_strings = ["test", "hello", "world", "summer_rain_chance", "location_weather"]
        
        def hash_strings():
            for test_string in test_strings:
                get_hash_from_string(test_string)
        
        benchmark(hash_strings)

    def test_hash_from_array_benchmark(self, benchmark, benchmark_seeds):
        """Benchmark hash from array performance."""
        test_arrays = [
            [1, 2, 3, 4, 5],
            [777, 0, 0, 0, 0],
            [0, 1, 2, 3, 4],
            [100, 200, 300, 400, 500],
        ]
        
        def hash_arrays():
            for test_array in test_arrays:
                get_hash_from_array(*test_array)
        
        benchmark(hash_arrays)

    def test_random_seed_benchmark(self, benchmark, benchmark_seeds):
        """Benchmark random seed generation performance."""
        test_cases = [
            (1, 2, 3, 4, 5, False),
            (777, 0, 0, 0, 0, False),
            (1, 2, 3, 4, 5, True),
            (777, 0, 0, 0, 0, True),
        ]
        
        def generate_random_seeds():
            for a, b, c, d, e, legacy in test_cases:
                get_random_seed(a, b, c, d, e, legacy)
        
        benchmark(generate_random_seeds)

    def test_weather_predictor_single_condition_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor with single condition."""
        predictor = WeatherPredictor()
        predictor.add_condition(spring_condition)
        
        def check_seeds():
            for seed in range(0, 1000):
                predictor.check(seed, False)
        
        benchmark(check_seeds)

    def test_weather_predictor_multiple_conditions_benchmark(self, benchmark, spring_condition, summer_condition, fall_condition):
        """Benchmark weather predictor with multiple conditions."""
        predictor = WeatherPredictor()
        conditions = [spring_condition, summer_condition, fall_condition]
        for condition in conditions:
            predictor.add_condition(condition)
        
        def check_seeds():
            for seed in range(0, 1000):
                predictor.check(seed, False)
        
        benchmark(check_seeds)

    def test_weather_predictor_medium_range_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor with medium seed range (100k max)."""
        predictor = WeatherPredictor()
        predictor.add_condition(spring_condition)
        
        def check_medium_range():
            # Test every 100th seed in range 0-100000
            for seed in range(0, 100001, 100):
                predictor.check(seed, False)
        
        benchmark(check_medium_range)

    def test_weather_predictor_legacy_random_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor with legacy random mode."""
        predictor = WeatherPredictor()
        predictor.add_condition(spring_condition)
        
        def check_seeds_legacy():
            for seed in range(0, 1000):
                predictor.check(seed, True)
        
        benchmark(check_seeds_legacy)

    def test_weather_predictor_consistency_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor consistency across multiple runs."""
        predictor = WeatherPredictor()
        predictor.add_condition(spring_condition)
        
        def check_consistency():
            # Run the same seeds multiple times
            test_seeds = list(range(0, 100))
            for _ in range(10):  # 10 iterations
                for seed in test_seeds:
                    predictor.check(seed, False)
        
        benchmark(check_consistency)

    @pytest.mark.parametrize("seed_range", [1000, 10000, 100000])
    def test_weather_predictor_scalability_benchmark(self, benchmark, spring_condition, seed_range):
        """Benchmark weather predictor scalability with different seed ranges (max 100k)."""
        predictor = WeatherPredictor()
        predictor.add_condition(spring_condition)
        
        def check_range():
            for seed in range(0, seed_range, max(1, seed_range // 1000)):  # Sample seeds
                predictor.check(seed, False)
        
        benchmark(check_range)

    def test_weather_predictor_gpu_consistency_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor consistency using GPU acceleration."""
        weather_conditions = [spring_condition]
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        
        def gpu_consistency_check():
            return asyncio.run(gpu_searcher.search_seeds_pure_gpu(0, 10000, 100))
        
        benchmark(gpu_consistency_check)

    def test_weather_predictor_gpu_scalability_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor scalability using GPU acceleration."""
        weather_conditions = [spring_condition]
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        
        def gpu_scalability_check():
            return asyncio.run(gpu_searcher.search_seeds_pure_gpu(0, 50000, 100))
        
        benchmark(gpu_scalability_check)

    def test_weather_predictor_memory_usage_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor memory usage."""
        predictor = WeatherPredictor()
        predictor.add_condition(spring_condition)
        
        def check_memory_intensive():
            # Create many conditions to test memory usage
            for i in range(100):
                condition = WeatherCondition(
                    season=Season.SPRING,
                    start_day=1,
                    end_day=10,
                    min_rain_days=5
                )
                predictor.add_condition(condition)
            
            # Then check some seeds
            for seed in range(0, 1000):
                predictor.check(seed, False)
        
        benchmark(check_memory_intensive)

    def test_hash_helper_comprehensive_benchmark(self, benchmark):
        """Comprehensive benchmark of hash helper functions."""
        def comprehensive_hash_test():
            # Test string hashing
            test_strings = ["test", "hello", "world", "summer_rain_chance", "location_weather"]
            for test_string in test_strings:
                get_hash_from_string(test_string)
            
            # Test array hashing
            test_arrays = [
                [1, 2, 3, 4, 5],
                [777, 0, 0, 0, 0],
                [0, 1, 2, 3, 4],
                [100, 200, 300, 400, 500],
            ]
            for test_array in test_arrays:
                get_hash_from_array(*test_array)
            
            # Test random seed generation
            test_cases = [
                (1, 2, 3, 4, 5, False),
                (777, 0, 0, 0, 0, False),
                (1, 2, 3, 4, 5, True),
                (777, 0, 0, 0, 0, True),
            ]
            for a, b, c, d, e, legacy in test_cases:
                get_random_seed(a, b, c, d, e, legacy)
        
        benchmark(comprehensive_hash_test)

    def test_weather_predictor_parallel_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor with parallel-like operations."""
        predictor = WeatherPredictor()
        predictor.add_condition(spring_condition)
        
        def parallel_like_check():
            # Simulate parallel operations by checking different seed ranges
            ranges = [
                (0, 1000),
                (1000, 2000),
                (2000, 3000),
                (3000, 4000),
                (4000, 5000),
            ]
            
            for start, end in ranges:
                for seed in range(start, end, 10):  # Sample every 10th seed
                    predictor.check(seed, False)
        
        benchmark(parallel_like_check)

    def test_weather_predictor_edge_cases_benchmark(self, benchmark):
        """Benchmark weather predictor with edge cases."""
        predictor = WeatherPredictor()
        
        # Test with various edge case conditions
        edge_conditions = [
            WeatherCondition(season=Season.SPRING, start_day=1, end_day=2, min_rain_days=1),
            WeatherCondition(season=Season.SPRING, start_day=1, end_day=3, min_rain_days=1),
            WeatherCondition(season=Season.SPRING, start_day=1, end_day=28, min_rain_days=1),
            WeatherCondition(season=Season.SPRING, start_day=1, end_day=28, min_rain_days=27),
        ]
        
        def check_edge_cases():
            for condition in edge_conditions:
                predictor._conditions.clear()
                predictor.add_condition(condition)
                
                # Test a few seeds
                for seed in range(0, 100):
                    predictor.check(seed, False)
        
        benchmark(check_edge_cases)

    def test_weather_predictor_consistency_benchmark(self, benchmark, spring_condition):
        """Benchmark weather predictor consistency across different modes."""
        predictor = WeatherPredictor()
        predictor.add_condition(spring_condition)
        
        def check_consistency_modes():
            test_seeds = list(range(0, 1000))
            
            # Test normal mode
            for seed in test_seeds:
                predictor.check(seed, False)
            
            # Test legacy mode
            for seed in test_seeds:
                predictor.check(seed, True)
        
        benchmark(check_consistency_modes)

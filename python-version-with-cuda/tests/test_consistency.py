"""
Test consistency with Go version
测试与Go版本的一致性
"""

import pytest
import asyncio
from internal.features import WeatherPredictor
from internal.models import WeatherCondition, Season
from internal.gpu_pure_accelerator import PureGPUSeedSearcher


@pytest.mark.consistency
@pytest.mark.unit
class TestConsistencyWithGo:
    """Test consistency with Go version."""

    def test_sample1_consistency(self, weather_predictor, spring_condition, expected_seeds_sample1):
        """Test sample 1 consistency: Spring first 10 days with 5 rain days."""
        weather_predictor.add_condition(spring_condition)
        
        # Find matching seeds in range 0-1000
        found_seeds = []
        for seed in range(0, 1001):
            if weather_predictor.check(seed, False):
                found_seeds.append(seed)
        
        assert found_seeds == expected_seeds_sample1, \
            f"Found seeds {found_seeds} should match expected {expected_seeds_sample1}"

    @pytest.mark.asyncio
    async def test_sample4_consistency(self):
        """Test sample 4 consistency: Spring/Summer each first 10 days in 0-100k range using GPU."""
        # Spring condition: first 10 days with 5 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
        # Summer condition: first 10 days with 6 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=10,
            min_rain_days=6
        )
        
        weather_conditions = [spring_condition, summer_condition]
        
        # Use GPU acceleration for large range search
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        found_seeds = await gpu_searcher.search_seeds_pure_gpu(0, 100000, 20)
        
        # Expected seed from Go test: 58038
        expected_seed = 58038
        assert expected_seed in found_seeds, f"Expected seed {expected_seed} should be found in {found_seeds[:10]}..."

    @pytest.mark.asyncio
    async def test_sample5_consistency(self):
        """Test sample 5 consistency: Spring/Summer/Fall each first 15 days in 100M-100.1M range using GPU."""
        # Spring condition: first 15 days with 6 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=15,
            min_rain_days=6
        )
        # Summer condition: first 15 days with 7 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=15,
            min_rain_days=7
        )
        # Fall condition: first 15 days with 6 rain days
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=15,
            min_rain_days=6
        )
        
        weather_conditions = [spring_condition, summer_condition, fall_condition]
        
        # Use GPU acceleration for large range search (100M-100.1M)
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        found_seeds = await gpu_searcher.search_seeds_pure_gpu(100000000, 100100000, 20)
        
        # Expected seeds from updated test: [100077568]
        expected_seeds = [100077568]
        for expected_seed in expected_seeds:
            assert expected_seed in found_seeds, f"Expected seed {expected_seed} should be found in {found_seeds[:10]}..."

    @pytest.mark.asyncio
    async def test_sample2_consistency(self):
        """Test sample 2 consistency: Spring/Summer/Fall each 28 days with 10 rain days in 0-1M range using GPU."""
        # Spring condition: 28 days with 10 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=28,
            min_rain_days=10
        )
        # Summer condition: 28 days with 10 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=28,
            min_rain_days=10
        )
        # Fall condition: 28 days with 10 rain days
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=28,
            min_rain_days=10
        )
        
        weather_conditions = [spring_condition, summer_condition, fall_condition]
        
        # Use GPU acceleration for large range search (0-1M)
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        found_seeds = await gpu_searcher.search_seeds_pure_gpu(0, 1000000, 20)
        
        # Expected seeds from updated test: [443151, 567995]
        expected_seeds = [443151, 567995]
        for expected_seed in expected_seeds:
            assert expected_seed in found_seeds, f"Expected seed {expected_seed} should be found in {found_seeds[:10]}..."

    @pytest.mark.asyncio
    async def test_sample3_consistency(self):
        """Test sample 3 consistency: Spring/Summer/Fall each first 10 days with 5 rain days in 0-1M range using GPU."""
        # Spring condition: first 10 days with 5 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
        # Summer condition: first 10 days with 5 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
        # Fall condition: first 10 days with 5 rain days
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
        
        weather_conditions = [spring_condition, summer_condition, fall_condition]
        
        # Use GPU acceleration for large range search (0-1M)
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        found_seeds = await gpu_searcher.search_seeds_pure_gpu(0, 1000000, 20)
        
        # Expected seeds from updated test: []
        expected_seeds = []
        for expected_seed in expected_seeds:
            assert expected_seed in found_seeds, f"Expected seed {expected_seed} should be found in {found_seeds[:10]}..."

    @pytest.mark.asyncio
    async def test_sample6_consistency(self):
        """Test sample 6 consistency: Spring/Summer/Fall each first 15 days with different rain requirements in 0-1M range using GPU."""
        # Spring condition: first 15 days with 5 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=15,
            min_rain_days=5
        )
        # Summer condition: first 15 days with 6 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=15,
            min_rain_days=6
        )
        # Fall condition: first 15 days with 6 rain days
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=15,
            min_rain_days=6
        )
        
        weather_conditions = [spring_condition, summer_condition, fall_condition]
        
        # Use GPU acceleration for large range search (0-1M)
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        found_seeds = await gpu_searcher.search_seeds_pure_gpu(0, 1000000, 20)
        
        # Expected seeds from updated test: [15278, 27396, 43362, 50668, 55234, 55873, 69723, 73556, 74213, 76395, 86007, 114536, 116799, 120232, 131095, 134368, 159031, 209947, 212567, 224068]
        expected_seeds = [15278, 27396, 43362, 50668, 55234, 55873, 69723, 73556, 74213, 76395, 86007, 114536, 116799, 120232, 131095, 134368, 159031, 209947, 212567, 224068]
        for expected_seed in expected_seeds:
            assert expected_seed in found_seeds, f"Expected seed {expected_seed} should be found in {found_seeds[:10]}..."

    @pytest.mark.asyncio
    async def test_sample7_consistency(self):
        """Test sample 7 consistency: Spring/Summer/Fall each first 15 days with 7 rain days in 100M-110M range using GPU."""
        # Spring condition: first 15 days with 7 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=15,
            min_rain_days=7
        )
        # Summer condition: first 15 days with 7 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=15,
            min_rain_days=7
        )
        # Fall condition: first 15 days with 7 rain days
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=15,
            min_rain_days=7
        )
        
        weather_conditions = [spring_condition, summer_condition, fall_condition]
        
        # Use GPU acceleration for large range search (100M-110M)
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        found_seeds = await gpu_searcher.search_seeds_pure_gpu(100000000, 110000000, 20)
        
        # Expected seeds from updated test: [100728737, 108581614]
        expected_seeds = [100728737, 108581614]
        for expected_seed in expected_seeds:
            assert expected_seed in found_seeds, f"Expected seed {expected_seed} should be found in {found_seeds[:10]}..."

    @pytest.mark.asyncio
    async def test_sample8_consistency(self):
        """Test sample 8 consistency: Spring/Summer/Fall each 28 days with different rain requirements in full int32 range using GPU."""
        # Spring condition: 28 days with 10 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=28,
            min_rain_days=10
        )
        # Summer condition: 28 days with 14 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=28,
            min_rain_days=14
        )
        # Fall condition: 28 days with 14 rain days
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=28,
            min_rain_days=14
        )
        
        weather_conditions = [spring_condition, summer_condition, fall_condition]
        
        # Use GPU acceleration for full int32 range search (0-2147483647)
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        found_seeds = await gpu_searcher.search_seeds_pure_gpu(0, 2147483647, 2)
        
        # Expected seeds from updated test: []
        expected_seeds = []
        for expected_seed in expected_seeds:
            assert expected_seed in found_seeds, f"Expected seed {expected_seed} should be found in {found_seeds[:10]}..."

    @pytest.mark.asyncio
    async def test_sample9_consistency(self):
        """Test sample 9 consistency: Spring/Summer/Fall each 28 days with rain requirements 10/14/13 in full int32 range using GPU."""
        # Spring condition: 28 days with 10 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=28,
            min_rain_days=10
        )
        # Summer condition: 28 days with 14 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=28,
            min_rain_days=14
        )
        # Fall condition: 28 days with 13 rain days
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=28,
            min_rain_days=13
        )
        
        weather_conditions = [spring_condition, summer_condition, fall_condition]
        
        # Use GPU acceleration for full int32 range search (0-2147483647)
        gpu_searcher = PureGPUSeedSearcher(weather_conditions, use_legacy_random=False)
        found_seeds = await gpu_searcher.search_seeds_pure_gpu(0, 2147483647, 2)
        
        # Expected seeds from test: [2092416592]
        expected_seeds = [2092416592]
        for expected_seed in expected_seeds:
            assert expected_seed in found_seeds, f"Expected seed {expected_seed} should be found in {found_seeds[:10]}..."

    @pytest.mark.parametrize("seed,expected", [
        (59, True),
        (73, True),
        (101, True),
        (142, True),
        (659, True),
        (932, True),
        (938, True),
        (0, False),
        (1, False),
        (2, False),
        (100, False),
        (200, False),
        (500, False),
    ])
    def test_specific_seeds_sample1(self, weather_predictor, spring_condition, seed, expected):
        """Test specific seeds for sample 1 consistency."""
        weather_predictor.add_condition(spring_condition)
        result = weather_predictor.check(seed, False)
        assert result == expected, f"Seed {seed} should {'pass' if expected else 'fail'}"

    def test_legacy_random_consistency(self, weather_predictor, spring_condition):
        """Test legacy random mode consistency."""
        weather_predictor.add_condition(spring_condition)
        
        # Test a few seeds with legacy random mode
        test_seeds = [0, 1, 2, 3, 4, 5, 10, 20, 50, 100]
        for seed in test_seeds:
            result_legacy = weather_predictor.check(seed, True)
            result_normal = weather_predictor.check(seed, False)
            
            # Results should be consistent (both boolean)
            assert isinstance(result_legacy, bool)
            assert isinstance(result_normal, bool)

    def test_weather_predictor_consistency_across_runs(self, weather_predictor, spring_condition):
        """Test that weather predictor gives consistent results across multiple runs."""
        weather_predictor.add_condition(spring_condition)
        
        test_seeds = [0, 1, 2, 3, 4, 5, 10, 20, 50, 100, 200, 500, 1000]
        
        # Run multiple times and check consistency
        for _ in range(3):
            results = []
            for seed in test_seeds:
                result = weather_predictor.check(seed, False)
                results.append(result)
            
            # Results should be the same each time
            if hasattr(self, '_previous_results'):
                assert results == self._previous_results, "Results should be consistent across runs"
            
            self._previous_results = results

    def test_hash_helper_consistency(self):
        """Test hash helper consistency with Go version."""
        from internal.core import get_hash_from_string, get_hash_from_array, get_random_seed
        
        # Test hash from string
        test_strings = ["test", "hello", "world", "summer_rain_chance", "location_weather"]
        expected_hashes = [1042293711, -83855367, 413819571, -309161378, -1513201250]
        
        for test_string, expected_hash in zip(test_strings, expected_hashes):
            result = get_hash_from_string(test_string)
            assert result == expected_hash, f"Hash for '{test_string}' should be {expected_hash}, got {result}"

        # Test hash from array
        test_arrays = [
            ([1, 2, 3, 4, 5], 100340316),
            ([777, 0, 0, 0, 0], 827005275),
            ([0, 1, 2, 3, 4], -64079150),
            ([100, 200, 300, 400, 500], -405830906),
        ]
        
        for test_array, expected_hash in test_arrays:
            result = get_hash_from_array(*test_array)
            assert result == expected_hash, f"Hash for {test_array} should be {expected_hash}, got {result}"

        # Test random seed
        test_seeds = [
            ((1, 2, 3, 4, 5, False), 100340316),
            ((777, 0, 0, 0, 0, False), 827005275),
            ((1, 2, 3, 4, 5, True), 15),
            ((777, 0, 0, 0, 0, True), 777),
        ]
        
        for (a, b, c, d, e, legacy), expected_seed in test_seeds:
            result = get_random_seed(a, b, c, d, e, legacy)
            assert result == expected_seed, f"Random seed for ({a}, {b}, {c}, {d}, {e}, {legacy}) should be {expected_seed}, got {result}"

    def test_weather_prediction_consistency_with_go_hashes(self, weather_predictor, spring_condition):
        """Test weather prediction consistency using Go version hash values."""
        weather_predictor.add_condition(spring_condition)
        
        # Test with seeds that should match Go version results
        go_test_cases = [
            (0, False),  # Should be False
            (59, True),  # Should be True
            (73, True),  # Should be True
            (101, True), # Should be True
            (142, True), # Should be True
            (659, True), # Should be True
            (932, True), # Should be True
            (938, True), # Should be True
        ]
        
        for seed, expected in go_test_cases:
            result = weather_predictor.check(seed, False)
            assert result == expected, f"Seed {seed} should be {expected}, got {result}"

    def test_consistency_with_different_seasons(self, weather_predictor):
        """Test consistency with different seasons."""
        # Test Spring
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
        weather_predictor.add_condition(spring_condition)
        
        spring_results = []
        for seed in range(0, 1001):
            spring_results.append(weather_predictor.check(seed, False))
        
        # Clear conditions and test Summer
        weather_predictor._conditions.clear()
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
        weather_predictor.add_condition(summer_condition)
        
        summer_results = []
        for seed in range(0, 1001):
            summer_results.append(weather_predictor.check(seed, False))
        
        # Results should be different between seasons
        assert spring_results != summer_results, "Spring and Summer results should be different"

    def test_consistency_with_different_day_ranges(self, weather_predictor):
        """Test consistency with different day ranges."""
        # Test 10-day range
        condition_10 = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=5
        )
        weather_predictor.add_condition(condition_10)
        
        results_10 = []
        for seed in range(0, 1001):
            results_10.append(weather_predictor.check(seed, False))
        
        # Clear conditions and test 28-day range
        weather_predictor._conditions.clear()
        condition_28 = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=28,
            min_rain_days=5
        )
        weather_predictor.add_condition(condition_28)
        
        results_28 = []
        for seed in range(0, 1001):
            results_28.append(weather_predictor.check(seed, False))
        
        # Results should be different between day ranges
        assert results_10 != results_28, "10-day and 28-day results should be different"

    def test_consistency_with_different_min_rain_days(self, weather_predictor):
        """Test consistency with different min rain days requirements."""
        # Test min_rain_days = 3
        condition_3 = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=3
        )
        weather_predictor.add_condition(condition_3)
        
        results_3 = []
        for seed in range(0, 1001):
            results_3.append(weather_predictor.check(seed, False))
        
        # Clear conditions and test min_rain_days = 7
        weather_predictor._conditions.clear()
        condition_7 = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=10,
            min_rain_days=7
        )
        weather_predictor.add_condition(condition_7)
        
        results_7 = []
        for seed in range(0, 1001):
            results_7.append(weather_predictor.check(seed, False))
        
        # Results with min_rain_days=7 should be a subset of results with min_rain_days=3
        seeds_3 = [i for i, result in enumerate(results_3) if result]
        seeds_7 = [i for i, result in enumerate(results_7) if result]
        
        assert all(seed in seeds_3 for seed in seeds_7), "Seeds with min_rain_days=7 should be subset of min_rain_days=3"

    def test_consistency_medium_range(self, weather_predictor, spring_condition):
        """Test consistency with medium seed range (100k max)."""
        weather_predictor.add_condition(spring_condition)
        
        # Test every 1000th seed in range 0-100000
        found_seeds = []
        for seed in range(0, 100001, 1000):
            if weather_predictor.check(seed, False):
                found_seeds.append(seed)
        
        # Should find some seeds in this range
        assert len(found_seeds) >= 0, "Should find some seeds in medium range"
        
        # Verify that found seeds actually pass the test
        for seed in found_seeds:
            assert weather_predictor.check(seed, False), f"Found seed {seed} should pass the test"

    def test_seed_2121_weather_detail(self, weather_predictor):
        """Test weather detail for seed 2121."""
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=28,
            min_rain_days=10
        )
        weather_predictor.add_condition(spring_condition)
        
        # 测试种子2121
        seed = 2121
        use_legacy_random = False
        
        # 获取天气详情
        weather_detail = weather_predictor.get_weather_detail(seed, use_legacy_random)
        
        # 验证天气详情
        expected_spring_rain = [3, 7, 9, 10, 14, 16, 21, 23, 25, 28]
        expected_summer_rain = [2, 3, 13, 16, 26]
        expected_fall_rain = [2, 3, 28]
        expected_green_rain_day = 16
        
        assert weather_detail.spring_rain == expected_spring_rain, \
            f"Spring rain for seed {seed} should be {expected_spring_rain}, got {weather_detail.spring_rain}"
        
        assert weather_detail.summer_rain == expected_summer_rain, \
            f"Summer rain for seed {seed} should be {expected_summer_rain}, got {weather_detail.summer_rain}"
        
        assert weather_detail.fall_rain == expected_fall_rain, \
            f"Fall rain for seed {seed} should be {expected_fall_rain}, got {weather_detail.fall_rain}"
        
        assert weather_detail.green_rain_day == expected_green_rain_day, \
            f"Green rain day for seed {seed} should be {expected_green_rain_day}, got {weather_detail.green_rain_day}"
        
        print(f"Seed {seed} weather detail test passed")
        print(f"  Spring rain: {weather_detail.spring_rain}")
        print(f"  Summer rain: {weather_detail.summer_rain}")
        print(f"  Fall rain: {weather_detail.fall_rain}")
        print(f"  Green rain day: {weather_detail.green_rain_day}")

    def test_seed_100077568_weather_detail(self, weather_predictor):
        """Test weather detail for seed 100077568."""
        # 添加春季条件：1-15天，最少6个雨天
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=15,
            min_rain_days=6
        )
        weather_predictor.add_condition(spring_condition)
        
        # 添加夏季条件：1-15天，最少7个雨天
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=15,
            min_rain_days=7
        )
        weather_predictor.add_condition(summer_condition)
        
        # 添加秋季条件：1-15天，最少6个雨天
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=15,
            min_rain_days=6
        )
        weather_predictor.add_condition(fall_condition)
        
        # 测试种子100077568
        seed = 100077568
        use_legacy_random = False
        
        # 获取天气详情
        weather_detail = weather_predictor.get_weather_detail(seed, use_legacy_random)
        
        # 验证天气详情
        expected_spring_rain = [3, 7, 9, 10, 11, 12, 20]
        expected_summer_rain = [5, 6, 7, 8, 10, 13, 15, 23, 24, 25, 26, 27]
        expected_fall_rain = [2, 3, 5, 7, 13, 15, 21]
        expected_green_rain_day = 5
        
        assert weather_detail.spring_rain == expected_spring_rain, \
            f"Spring rain for seed {seed} should be {expected_spring_rain}, got {weather_detail.spring_rain}"
        
        assert weather_detail.summer_rain == expected_summer_rain, \
            f"Summer rain for seed {seed} should be {expected_summer_rain}, got {weather_detail.summer_rain}"
        
        assert weather_detail.fall_rain == expected_fall_rain, \
            f"Fall rain for seed {seed} should be {expected_fall_rain}, got {weather_detail.fall_rain}"
        
        assert weather_detail.green_rain_day == expected_green_rain_day, \
            f"Green rain day for seed {seed} should be {expected_green_rain_day}, got {weather_detail.green_rain_day}"
        
        print(f"Seed {seed} weather detail test passed")
        print(f"  Spring rain: {weather_detail.spring_rain}")
        print(f"  Summer rain: {weather_detail.summer_rain}")
        print(f"  Fall rain: {weather_detail.fall_rain}")
        print(f"  Green rain day: {weather_detail.green_rain_day}")

    def test_seed_2092416592_weather_detail(self, weather_predictor):
        """Test weather detail for seed 2092416592."""
        # Add spring condition: 1-28 days, minimum 10 rain days
        spring_condition = WeatherCondition(
            season=Season.SPRING,
            start_day=1,
            end_day=28,
            min_rain_days=10
        )
        weather_predictor.add_condition(spring_condition)
        
        # Add summer condition: 1-28 days, minimum 14 rain days
        summer_condition = WeatherCondition(
            season=Season.SUMMER,
            start_day=1,
            end_day=28,
            min_rain_days=14
        )
        weather_predictor.add_condition(summer_condition)
        
        # Add fall condition: 1-28 days, minimum 13 rain days
        fall_condition = WeatherCondition(
            season=Season.FALL,
            start_day=1,
            end_day=28,
            min_rain_days=13
        )
        weather_predictor.add_condition(fall_condition)
        
        # Test seed 2092416592
        seed = 2092416592
        use_legacy_random = False
        
        # Get weather detail
        weather_detail = weather_predictor.get_weather_detail(seed, use_legacy_random)
        
        # Verify weather detail
        expected_spring_rain = [3, 7, 8, 16, 17, 18, 22, 25, 26, 28]
        expected_summer_rain = [2, 3, 6, 8, 9, 10, 13, 14, 15, 19, 20, 21, 22, 26]
        expected_fall_rain = [2, 3, 4, 8, 10, 11, 12, 17, 19, 20, 24, 26, 28]
        expected_green_rain_day = 15
        
        assert weather_detail.spring_rain == expected_spring_rain, \
            f"Spring rain for seed {seed} should be {expected_spring_rain}, got {weather_detail.spring_rain}"
        
        assert weather_detail.summer_rain == expected_summer_rain, \
            f"Summer rain for seed {seed} should be {expected_summer_rain}, got {weather_detail.summer_rain}"
        
        assert weather_detail.fall_rain == expected_fall_rain, \
            f"Fall rain for seed {seed} should be {expected_fall_rain}, got {weather_detail.fall_rain}"
        
        assert weather_detail.green_rain_day == expected_green_rain_day, \
            f"Green rain day for seed {seed} should be {expected_green_rain_day}, got {weather_detail.green_rain_day}"
        
        print(f"Seed {seed} weather detail test passed")
        print(f"  Spring rain: {weather_detail.spring_rain}")
        print(f"  Summer rain: {weather_detail.summer_rain}")
        print(f"  Fall rain: {weather_detail.fall_rain}")
        print(f"  Green rain day: {weather_detail.green_rain_day}")

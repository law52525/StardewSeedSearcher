"""
Search features implementation
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from internal.models import WeatherCondition, Season
from internal.core import get_random_seed, get_hash_from_string


class SearchFeature(ABC):
    """Interface for all search features"""
    
    @abstractmethod
    def name(self) -> str:
        """Return feature name"""
        pass
    
    @abstractmethod
    def is_enabled(self) -> bool:
        """Return whether this feature is enabled"""
        pass
    
    @abstractmethod
    def set_enabled(self, enabled: bool) -> None:
        """Set whether this feature is enabled"""
        pass
    
    @abstractmethod
    def check(self, game_id: int, use_legacy_random: bool) -> bool:
        """Check if seed meets this feature's filtering conditions
        Args:
            game_id: Game seed
            use_legacy_random: Whether to use legacy random mode
        Returns:
            True if conditions are met, False otherwise
        """
        pass
    
    @abstractmethod
    def get_config_description(self) -> str:
        """Return configuration description for this feature"""
        pass


class WeatherPredictor(SearchFeature):
    """Weather prediction functionality"""
    
    # Pre-computed hash constants to avoid repeated calculations
    _summer_rain_chance_hash = get_hash_from_string("summer_rain_chance")
    _location_weather_hash = get_hash_from_string("location_weather")
    
    def __init__(self):
        self._conditions: List[WeatherCondition] = []
        self._enabled = True
        # Reuse weather map to reduce memory allocation
        self._weather_cache: Dict[int, bool] = {}
    
    def name(self) -> str:
        return "天气预测"
    
    def is_enabled(self) -> bool:
        return self._enabled
    
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
    
    def add_condition(self, condition: WeatherCondition) -> None:
        """Add weather condition"""
        self._conditions.append(condition)
    
    def get_conditions(self) -> List[WeatherCondition]:
        """Return all conditions"""
        return self._conditions.copy()
    
    def check(self, game_id: int, use_legacy_random: bool) -> bool:
        """Check if seed meets weather filtering conditions"""
        # If no conditions, consider as no filtering (all pass)
        if not self._conditions:
            return True
        
        # Predict weather for first year spring/summer/fall (days 1-84)
        all_weather = self.predict_weather(game_id, use_legacy_random)
        
        # Check each condition
        for condition in self._conditions:
            rain_count = self._count_rain_in_range(all_weather, condition)
            if rain_count < condition.min_rain_days:
                return False
        
        return True
    
    def get_config_description(self) -> str:
        if not self._conditions:
            return "无筛选条件"
        
        descriptions = [str(condition) for condition in self._conditions]
        return str(descriptions)
    
    def _count_rain_in_range(self, weather: Dict[int, bool], condition: WeatherCondition) -> int:
        """Count rainy days in specified range"""
        count = 0
        for day in range(condition.absolute_start_day, condition.absolute_end_day + 1):
            if weather.get(day, False):
                count += 1
        return count
    
    def predict_weather(self, game_id: int, use_legacy_random: bool) -> Dict[int, bool]:
        """Predict weather for first year spring/summer/fall (days 1-84)"""
        # Clear cache and reuse
        self._weather_cache.clear()

        
        # Summer special: Green rain day determination
        year = 1  # First year
        green_rain_seed = get_random_seed(year * 777, game_id, 0, 0, 0, use_legacy_random)
        # Use same Random.Next() logic as C#
        green_rain_days = [5, 6, 7, 14, 15, 16, 18, 23]
        green_rain_day = green_rain_days[self._random_next(green_rain_seed, len(green_rain_days))]
        
        for absolute_day in range(1, 85):  # 1-84 inclusive
            season = (absolute_day - 1) // 28  # 0=Spring, 1=Summer, 2=Fall
            day_of_month = ((absolute_day - 1) % 28) + 1
            
            is_rain = self._is_rainy_day(season, day_of_month, absolute_day, game_id, use_legacy_random, green_rain_day)
            self._weather_cache[absolute_day] = is_rain
        
        return self._weather_cache
    
    def _is_rainy_day(self, season: int, day_of_month: int, absolute_day: int, game_id: int, use_legacy_random: bool, green_rain_day: int) -> bool:
        """Determine if a specific day is rainy"""
        # Fixed weather rules
        if day_of_month == 1:
            return False  # Sunny
        
        if season == 0:  # Spring
            if day_of_month in [2, 4, 5]:
                return False  # Sunny
            if day_of_month == 3:
                return True  # Rainy
            if day_of_month in [13, 24]:
                return False  # Festival fixed sunny
            # Spring continues to general logic below
            
        elif season == 1:  # Summer
            if day_of_month == green_rain_day:
                return True  # Green rain (counts as rainy)
            if day_of_month in [11, 28]:
                return False  # Festival fixed sunny
            if day_of_month % 13 == 0:  # Days 13, 26
                return True  # Thunderstorm (counts as rainy)
            
            # Normal rain: probability increases with date
            rain_seed = get_random_seed(absolute_day - 1, game_id // 2, self._summer_rain_chance_hash, 0, 0, use_legacy_random)
            # Use same Random.NextDouble() logic as C#
            normalized_seed = self._random_next_double(rain_seed)
            rain_chance = 0.12 + 0.003 * (day_of_month - 1)
            return normalized_seed < rain_chance
            
        elif season == 2:  # Fall
            if day_of_month in [16, 27]:
                return False  # Festival fixed sunny
            # Fall continues to general logic below
        
        # Spring and Fall normal days: 18.3% probability
        seed = get_random_seed(self._location_weather_hash, game_id, absolute_day - 1, 0, 0, use_legacy_random)
        # Use same Random.NextDouble() logic as C#
        normalized_seed = self._random_next_double(seed)
        return normalized_seed < 0.183
    
    def _random_next(self, seed: int, max_value: int) -> int:
        """Simulate C#'s Random.Next(maxValue) method
        Uses same formula as .NET 9 Net5CompatSeedImpl
        """
        if max_value <= 0:
            return 0
        
        # Use same formula as random_next_double
        first_rand = self._get_first_rand(seed)
        
        # C#'s Random.Next() uses different logic
        # It uses (int)((long)firstRand * maxValue / int32Max)
        # instead of simple modulo operation
        int32_max = 2147483647
        return int((first_rand * max_value) // int32_max)
    
    def _get_first_rand(self, seed: int) -> int:
        """Get first random number using .NET Random.Next()'s exact formula"""
        multiplier = 1121899819
        constant = 1559595546
        int32_max = 2147483647
        
        # C#'s Random constructor takes absolute value of negative seeds
        if seed < 0:
            seed = -seed
        
        # Use int64 to avoid overflow, then convert to int32
        # Calculate y = (1121899819 * x + 1559595546) % 2147483647
        result = (multiplier * seed + constant) % int32_max
        if result < 0:
            result += int32_max
        
        return result
    
    def _random_next_double(self, seed: int) -> float:
        """Simulate C#'s Random.NextDouble() method
        Returns float in range [0.0, 1.0)
        """
        # Get first random number
        first_rand = self._get_first_rand(seed)
        
        # C#'s NextDouble() = Sample() * (1.0 / int.MaxValue)
        # where Sample() returns integer in range [0, int.MaxValue)
        return first_rand / 0x7FFFFFFF
    
    def predict_spring_rain(self, game_id: int, use_legacy_random: bool) -> List[int]:
        """Predict spring rainy days (kept for testing scripts)"""
        weather = self.predict_weather(game_id, use_legacy_random)
        rainy_days = []
        
        for day in range(1, 29):  # 1-28
            if weather.get(day, False):
                rainy_days.append(day)
        
        return rainy_days
    
    def get_weather_detail(self, game_id: int, use_legacy_random: bool):
        """Get detailed weather information"""
        from internal.models import WeatherDetail
        
        weather = self.predict_weather(game_id, use_legacy_random)
        
        # Initialize rainy days for each season
        spring_rain = []
        summer_rain = []
        fall_rain = []
        
        # Get green rain day
        green_rain_day = self._get_green_rain_day(game_id, use_legacy_random)
        
        # Iterate through all weather, categorize by season
        for absolute_day in range(1, 85):  # 1-84 inclusive
            if weather.get(absolute_day, False):
                season = (absolute_day - 1) // 28  # 0=Spring, 1=Summer, 2=Fall
                day_of_month = ((absolute_day - 1) % 28) + 1
                
                if season == 0:  # Spring
                    spring_rain.append(day_of_month)
                elif season == 1:  # Summer
                    summer_rain.append(day_of_month)
                elif season == 2:  # Fall
                    fall_rain.append(day_of_month)
        
        return WeatherDetail(
            spring_rain=spring_rain,
            summer_rain=summer_rain,
            fall_rain=fall_rain,
            green_rain_day=green_rain_day
        )
    
    def _get_green_rain_day(self, game_id: int, use_legacy_random: bool) -> int:
        """Get green rain day"""
        year = 1  # First year
        green_rain_seed = get_random_seed(year * 777, game_id, 0, 0, 0, use_legacy_random)
        green_rain_days = [5, 6, 7, 14, 15, 16, 18, 23]
        return green_rain_days[self._random_next(green_rain_seed, len(green_rain_days))]
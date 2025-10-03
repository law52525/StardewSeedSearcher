"""
Data models for Stardew Valley Seed Searcher
"""

from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict


class Season(str, Enum):
    """Game seasons"""
    SPRING = "Spring"
    SUMMER = "Summer"
    FALL = "Fall"


class WeatherCondition(BaseModel):
    """Weather filtering condition"""
    model_config = ConfigDict(populate_by_name=True)
    
    season: Season
    start_day: int = Field(..., ge=1, le=28, alias="startDay", description="Start day of the season (1-28)")
    end_day: int = Field(..., ge=1, le=28, alias="endDay", description="End day of the season (1-28)")
    min_rain_days: int = Field(..., ge=1, alias="minRainDays", description="Minimum number of rainy days required")
    
    def model_post_init(self, __context):
        """Post-initialization validation"""
        # Validate that start_day <= end_day
        if self.start_day > self.end_day:
            raise ValueError("start_day must be less than or equal to end_day")
        # Validate that min_rain_days is not greater than the day range
        day_count = self.end_day - self.start_day + 1
        if self.min_rain_days > day_count:
            raise ValueError(f"min_rain_days ({self.min_rain_days}) cannot be greater than the day range ({day_count})")
        # Additional validation: min_rain_days should be reasonable (not equal to day_count)
        if self.min_rain_days == day_count:
            raise ValueError(f"min_rain_days ({self.min_rain_days}) cannot equal the day range ({day_count}) - this would require every day to be rainy")
    
    @property
    def absolute_start_day(self) -> int:
        """Get absolute start day (1-84)"""
        season_offset = {"Spring": 0, "Summer": 28, "Fall": 56}
        return season_offset[self.season] + self.start_day
    
    @property
    def absolute_end_day(self) -> int:
        """Get absolute end day (1-84)"""
        season_offset = {"Spring": 0, "Summer": 28, "Fall": 56}
        return season_offset[self.season] + self.end_day
    
    def __str__(self) -> str:
        """Human-readable string representation"""
        season_names = {"Spring": "春", "Summer": "夏", "Fall": "秋"}
        season_name = season_names[self.season]
        return f"{season_name}{self.start_day}-{season_name}{self.end_day}: 最少{self.min_rain_days}个雨天"


class SearchRequest(BaseModel):
    """Search request from frontend"""
    model_config = ConfigDict(populate_by_name=True)
    
    start_seed: int = Field(..., ge=0, alias="startSeed", description="Starting seed number")
    end_seed: int = Field(..., ge=0, le=2147483647, alias="endSeed", description="Ending seed number")
    use_legacy_random: bool = Field(False, alias="useLegacyRandom", description="Whether to use legacy random mode")
    weather_conditions: List[WeatherCondition] = Field(default_factory=list, alias="weatherConditions", description="Weather filtering conditions")
    output_limit: int = Field(20, ge=1, alias="outputLimit", description="Maximum number of results to return")
    
    def __init__(self, **data):
        super().__init__(**data)
        if self.start_seed >= self.end_seed:
            raise ValueError("end_seed must be greater than start_seed")


class SearchResponse(BaseModel):
    """Search request response"""
    message: str


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "ok"
    version: str = "1.0"


class WebSocketMessage(BaseModel):
    """Base WebSocket message"""
    type: str


class StartMessage(WebSocketMessage):
    """Search start message"""
    model_config = ConfigDict(populate_by_name=True)
    
    type: str = "start"
    total: int


class ProgressMessage(WebSocketMessage):
    """Progress update message"""
    model_config = ConfigDict(populate_by_name=True)
    
    type: str = "progress"
    checked_count: int = Field(alias="checkedCount")
    total: int
    progress: float
    speed: float
    elapsed: float


class FoundMessage(WebSocketMessage):
    """Found seed message"""
    model_config = ConfigDict(populate_by_name=True)
    
    type: str = "found"
    seed: int


class CompleteMessage(WebSocketMessage):
    """Search complete message"""
    model_config = ConfigDict(populate_by_name=True)
    
    type: str = "complete"
    total_found: int = Field(alias="totalFound")
    elapsed: float

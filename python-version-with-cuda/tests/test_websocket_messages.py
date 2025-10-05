"""
Test WebSocket message functionality
测试WebSocket消息功能
"""

import pytest
import json
from internal.models import StartMessage, ProgressMessage, FoundMessage, CompleteMessage


@pytest.mark.websocket
@pytest.mark.unit
class TestWebSocketMessages:
    """Test WebSocket message serialization and deserialization."""

    def test_start_message_creation(self):
        """Test StartMessage creation and serialization."""
        start_msg = StartMessage(total=1000)
        
        assert start_msg.type == "start"
        assert start_msg.total == 1000

    def test_start_message_serialization(self):
        """Test StartMessage JSON serialization."""
        start_msg = StartMessage(total=1000)
        start_json = start_msg.model_dump_json(by_alias=True)
        
        # Parse JSON to verify structure
        data = json.loads(start_json)
        assert data["type"] == "start"
        assert data["total"] == 1000

    def test_progress_message_creation(self):
        """Test ProgressMessage creation."""
        progress_msg = ProgressMessage(
            checked_count=100,
            total=1000,
            progress=10.0,
            speed=50.0,
            elapsed=2.0
        )
        
        assert progress_msg.type == "progress"
        assert progress_msg.checked_count == 100
        assert progress_msg.total == 1000
        assert progress_msg.progress == 10.0
        assert progress_msg.speed == 50.0
        assert progress_msg.elapsed == 2.0

    def test_progress_message_serialization(self):
        """Test ProgressMessage JSON serialization with camelCase aliases."""
        progress_msg = ProgressMessage(
            checked_count=100,
            total=1000,
            progress=10.0,
            speed=50.0,
            elapsed=2.0
        )
        progress_json = progress_msg.model_dump_json(by_alias=True)
        
        # Parse JSON to verify structure
        data = json.loads(progress_json)
        assert data["type"] == "progress"
        assert data["checkedCount"] == 100  # Should use camelCase alias
        assert data["total"] == 1000
        assert data["progress"] == 10.0
        assert data["speed"] == 50.0
        assert data["elapsed"] == 2.0

    def test_found_message_creation(self):
        """Test FoundMessage creation."""
        found_msg = FoundMessage(seed=12345)
        
        assert found_msg.type == "found"
        assert found_msg.seed == 12345

    def test_found_message_serialization(self):
        """Test FoundMessage JSON serialization."""
        found_msg = FoundMessage(seed=12345)
        found_json = found_msg.model_dump_json(by_alias=True)
        
        # Parse JSON to verify structure
        data = json.loads(found_json)
        assert data["type"] == "found"
        assert data["seed"] == 12345

    def test_complete_message_creation(self):
        """Test CompleteMessage creation."""
        complete_msg = CompleteMessage(
            total_found=5,
            elapsed=10.5
        )
        
        assert complete_msg.type == "complete"
        assert complete_msg.total_found == 5
        assert complete_msg.elapsed == 10.5

    def test_complete_message_serialization(self):
        """Test CompleteMessage JSON serialization with camelCase aliases."""
        complete_msg = CompleteMessage(
            total_found=5,
            elapsed=10.5
        )
        complete_json = complete_msg.model_dump_json(by_alias=True)
        
        # Parse JSON to verify structure
        data = json.loads(complete_json)
        assert data["type"] == "complete"
        assert data["totalFound"] == 5  # Should use camelCase alias
        assert data["elapsed"] == 10.5

    @pytest.mark.parametrize("total", [0, 100, 1000, 1000000])
    def test_start_message_various_totals(self, total):
        """Test StartMessage with various total values."""
        start_msg = StartMessage(total=total)
        assert start_msg.total == total
        
        data = json.loads(start_msg.model_dump_json(by_alias=True))
        assert data["total"] == total

    @pytest.mark.parametrize("checked_count,total,progress", [
        (0, 1000, 0.0),
        (100, 1000, 10.0),
        (500, 1000, 50.0),
        (1000, 1000, 100.0),
    ])
    def test_progress_message_various_values(self, checked_count, total, progress):
        """Test ProgressMessage with various values."""
        progress_msg = ProgressMessage(
            checked_count=checked_count,
            total=total,
            progress=progress,
            speed=50.0,
            elapsed=2.0
        )
        
        assert progress_msg.checked_count == checked_count
        assert progress_msg.total == total
        assert progress_msg.progress == progress

    @pytest.mark.parametrize("seed", [0, 1, 100, 1000, 1000000])
    def test_found_message_various_seeds(self, seed):
        """Test FoundMessage with various seed values."""
        found_msg = FoundMessage(seed=seed)
        assert found_msg.seed == seed
        
        data = json.loads(found_msg.model_dump_json(by_alias=True))
        assert data["seed"] == seed

    @pytest.mark.parametrize("total_found,elapsed", [
        (0, 0.0),
        (1, 1.5),
        (10, 5.0),
        (100, 30.0),
    ])
    def test_complete_message_various_values(self, total_found, elapsed):
        """Test CompleteMessage with various values."""
        complete_msg = CompleteMessage(
            total_found=total_found,
            elapsed=elapsed
        )
        
        assert complete_msg.total_found == total_found
        assert complete_msg.elapsed == elapsed

    def test_message_roundtrip_serialization(self):
        """Test message serialization and deserialization roundtrip."""
        # Test StartMessage
        original_start = StartMessage(total=1000)
        start_json = original_start.model_dump_json(by_alias=True)
        start_data = json.loads(start_json)
        assert start_data["type"] == "start"
        assert start_data["total"] == 1000

        # Test ProgressMessage
        original_progress = ProgressMessage(
            checked_count=100,
            total=1000,
            progress=10.0,
            speed=50.0,
            elapsed=2.0
        )
        progress_json = original_progress.model_dump_json(by_alias=True)
        progress_data = json.loads(progress_json)
        assert progress_data["type"] == "progress"
        assert progress_data["checkedCount"] == 100

        # Test FoundMessage
        original_found = FoundMessage(seed=12345)
        found_json = original_found.model_dump_json(by_alias=True)
        found_data = json.loads(found_json)
        assert found_data["type"] == "found"
        assert found_data["seed"] == 12345

        # Test CompleteMessage
        original_complete = CompleteMessage(
            total_found=5,
            elapsed=10.5
        )
        complete_json = original_complete.model_dump_json(by_alias=True)
        complete_data = json.loads(complete_json)
        assert complete_data["type"] == "complete"
        assert complete_data["totalFound"] == 5

    def test_message_validation(self):
        """Test message validation with invalid values."""
        # Test that negative values are accepted (they might be valid in some contexts)
        start_msg = StartMessage(total=-1)
        assert start_msg.total == -1
        
        progress_msg = ProgressMessage(
            checked_count=-1,
            total=1000,
            progress=10.0,
            speed=50.0,
            elapsed=2.0
        )
        assert progress_msg.checked_count == -1
        
        found_msg = FoundMessage(seed=-1)
        assert found_msg.seed == -1
        
        complete_msg = CompleteMessage(
            total_found=-1,
            elapsed=10.5
        )
        assert complete_msg.total_found == -1

    def test_message_type_consistency(self):
        """Test that message types are consistent."""
        start_msg = StartMessage(total=1000)
        progress_msg = ProgressMessage(
            checked_count=100,
            total=1000,
            progress=10.0,
            speed=50.0,
            elapsed=2.0
        )
        found_msg = FoundMessage(seed=12345)
        complete_msg = CompleteMessage(
            total_found=5,
            elapsed=10.5
        )

        assert start_msg.type == "start"
        assert progress_msg.type == "progress"
        assert found_msg.type == "found"
        assert complete_msg.type == "complete"

    def test_websocket_message_samples(self, websocket_message_samples):
        """Test WebSocket message samples from fixtures."""
        # Test start message
        start_msg = StartMessage(total=websocket_message_samples["start"]["total"])
        start_data = json.loads(start_msg.model_dump_json(by_alias=True))
        assert start_data == websocket_message_samples["start"]

        # Test progress message
        progress_data = websocket_message_samples["progress"]
        progress_msg = ProgressMessage(
            checked_count=progress_data["checkedCount"],
            total=progress_data["total"],
            progress=progress_data["progress"],
            speed=progress_data["speed"],
            elapsed=progress_data["elapsed"]
        )
        progress_result = json.loads(progress_msg.model_dump_json(by_alias=True))
        assert progress_result == progress_data

        # Test found message
        found_data = websocket_message_samples["found"]
        from internal.models import WeatherDetail
        weather_detail = WeatherDetail(
            spring_rain=found_data["weatherDetail"]["springRain"],
            summer_rain=found_data["weatherDetail"]["summerRain"],
            fall_rain=found_data["weatherDetail"]["fallRain"],
            green_rain_day=found_data["weatherDetail"]["greenRainDay"]
        )
        found_msg = FoundMessage(seed=found_data["seed"], weather_detail=weather_detail)
        found_result = json.loads(found_msg.model_dump_json(by_alias=True))
        assert found_result == found_data

        # Test complete message
        complete_data = websocket_message_samples["complete"]
        complete_msg = CompleteMessage(
            total_found=complete_data["totalFound"],
            elapsed=complete_data["elapsed"]
        )
        complete_result = json.loads(complete_msg.model_dump_json(by_alias=True))
        assert complete_result == complete_data

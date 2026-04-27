from deduplicator import InMemoryDeduplicator
from runner import IngestionRunner


class FakeSource:
    def __init__(self, data: list[str]):
        self.fake_data = data

    def fetch(self) -> list[str]:
        return self.fake_data


class FakeTransformer:
    def transform(self, raw_data: list[str]):
        return raw_data


class FakePublisher:
    def __init__(self):
        self.published = None

    def publish(self, measurements):
        self.published = measurements


class FakeMeasurement:
    def __init__(self, sensor_id: str, timestamp: str, value: int):
        self.sensor_id = sensor_id
        self.timestamp = timestamp
        self.value = value


def test_runner_run_once_filters_duplicates_with_inmemory_deduplicator():
    publisher = FakePublisher()

    measurements = [
        FakeMeasurement(sensor_id="s1", timestamp="t1", value=1), # GOOD
        FakeMeasurement(sensor_id="s1", timestamp="t1", value=1), # DUPLICATE
        FakeMeasurement(sensor_id="s1", timestamp="t2", value=2), # GOOD
        FakeMeasurement(sensor_id="s1", timestamp="t3", value=3), # GOOD
        FakeMeasurement(sensor_id="s1", timestamp="t3", value=5), # DUPLICATE
    ]

    runner = IngestionRunner(
        source=FakeSource(measurements),
        transformer=FakeTransformer(),
        publisher=publisher,
        deduplicator=InMemoryDeduplicator(),
    )

    result = runner.run_once()

    assert len(result) == 3
    assert result[0].sensor_id == "s1"
    assert result[0].timestamp == "t1"
    assert result[0].value == 1
    assert result[1].sensor_id == "s1"
    assert result[1].timestamp == "t2"
    assert result[1].value == 2
    assert result[2].sensor_id == "s1"
    assert result[2].timestamp == "t3"
    assert result[2].value == 3

    assert publisher.published == result

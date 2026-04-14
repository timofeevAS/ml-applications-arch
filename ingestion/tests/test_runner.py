from runner import IngestionRunner

class FakeSource:
    def __init__(self, data: list[str]):
        self.fake_data = data

    def fetch(self) -> list[str]:
        return self.fake_data

class FakeTransformer:
    def transform(self, raw_data: list[str]):
        return [f"<{x}>" for x in raw_data]

class FakePublisher:
    def __init__(self):
        self.published = None

    def publish(self, measurements):
        self.published = measurements

def test_runner_run_once_publishes_measurements():
    runner = IngestionRunner(
        source=FakeSource(["1","2","3"]),
        transformer=FakeTransformer(),
        publisher=FakePublisher(),
    )

    result = runner.run_once()

    assert result == ["<1>", "<2>" , "<3>"]
    assert runner.publisher.published == ["<1>", "<2>" , "<3>"]

def test_runner_run_once_empty_mesurements():
    publisher = FakePublisher()

    runner = IngestionRunner(
        source=FakeSource([]),
        transformer=FakeTransformer(),
        publisher=publisher,
    )

    result = runner.run_once()

    assert result == []
    assert publisher.published is None # Ingestion runner ignore empty measurements lists
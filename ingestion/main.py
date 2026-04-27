import time
from datetime import datetime

from deduplicator import InMemoryDeduplicator
from publisher.stdout import StdoutPublisher
from runner import IngestionRunner
from settings import settings
from sources.digitraffic import DigitrafficHistoryReplaySource
from transformers.digitraffic import DigitrafficTransformer


def main() -> None:
    runner = IngestionRunner(
        source=DigitrafficHistoryReplaySource(replay_start=datetime.now(), csv_paths=settings.digitraffic_sources),
        transformer=DigitrafficTransformer(),
        publisher=StdoutPublisher(),
        deduplicator=InMemoryDeduplicator(),
    )

    # Using .env variable.
    fetch_interval = settings.polling_seconds_timeout

    while True:
        start = time.time()

        try:
            runner.run_once()
        except Exception as e:
            print(f"[Runner] error: {e}")

        # A fair way to calculate latency, taking pipeline delay into account.
        elapsed = time.time() - start
        sleep_time = max(0, fetch_interval - elapsed)
        time.sleep(sleep_time)


if __name__ == "__main__":
    main()

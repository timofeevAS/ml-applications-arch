import time

from deduplicator import InMemoryDeduplicator
from publisher.stdout import StdoutPublisher
from runner import IngestionRunner
from sources.digitraffic import DigitrafficSource
from transformers.digitraffic import DigitrafficTransformer
from settings import settings


def main() -> None:
    STATION_IDS=[20002]

    runner = IngestionRunner(
        source=DigitrafficSource(station_ids=STATION_IDS),
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
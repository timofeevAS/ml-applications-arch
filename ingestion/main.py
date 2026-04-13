from deduplicator import InMemoryDeduplicator
from publisher.stdout import StdoutPublisher
from runner import IngestionRunner
from sources.digitraffic import DigitrafficSource
from transformers.digitraffic import DigitrafficTransformer


def main() -> None:
    runner = IngestionRunner(
        source=DigitrafficSource(),
        transformer=DigitrafficTransformer(),
        publisher=StdoutPublisher(),
        deduplicator=InMemoryDeduplicator(),
    )

    runner.run_once()


if __name__ == "__main__":
    main()
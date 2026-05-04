from dataclasses import dataclass

from deduplicator import Deduplicator
from publisher.base import Publisher
from sources.base import Source
from transformers.base import Transformer


@dataclass(slots=True)
class IngestionRunner:
    source: Source
    transformer: Transformer
    publisher: Publisher
    deduplicator: Deduplicator | None = None

    def run_once(self) -> list:
        raw_data = self.source.fetch()
        measurements = self.transformer.transform(raw_data)

        if self.deduplicator is not None:
            measurements = [
                measurement
                for measurement in measurements
                if self.deduplicator.is_new(measurement)
            ]

        if measurements:
            self.publisher.publish(measurements)

        return measurements

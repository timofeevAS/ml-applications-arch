from dataclasses import dataclass

from publisher.base import Publisher
from sources.base import Source
from transformers.base import Transformer


@dataclass(slots=True)
class IngestionRunner:
    source: Source
    transformer: Transformer
    publisher: Publisher

    def run_once(self) -> list:
        raw_data = self.source.fetch()
        measurements = self.transformer.transform(raw_data)

        if measurements:
            self.publisher.publish(measurements)

        return measurements
import json
from dataclasses import asdict

from publisher.base import Publisher
from transformers.base import Measurment


class StdoutPublisher(Publisher):
    def publish(self, data: list[Measurment]) -> None:
        for item in data:
            print(json.dumps(asdict(item)))
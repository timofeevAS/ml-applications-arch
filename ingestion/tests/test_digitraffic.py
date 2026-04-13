import json

import pytest
from publisher.stdout import StdoutPublisher
from sources.digitraffic import DigitrafficSource, DigitrafficTrafficFlowHourlySensor
from transformers.base import Measurment
from transformers.digitraffic import DigitrafficTransformer

@pytest.mark.parametrize(
    "station_ids, expected_len",
    [
        ([], 0),
        ([20002], 1),
        ([20002, 23001], 2),
    ],
)
@pytest.mark.external
def test_digitraffic_fetch_smoke(station_ids, expected_len):
    source = DigitrafficSource(station_ids=station_ids)
    data = source.fetch()

    assert len(data) == expected_len

def test_digitraffic_transform():
    transformer = DigitrafficTransformer()

    result = transformer.transform(
        [
            DigitrafficTrafficFlowHourlySensor(
                station_id=20002,
                sensor_value=312,
                measured_time='2026-04-10T20:52:03Z', 
                unit='kpl/h'),
            DigitrafficTrafficFlowHourlySensor(
                station_id=23001,
                sensor_value=32,
                measured_time='2026-04-10T20:52:03Z', 
                unit='kpl/h')   
        ]
        )

    assert len(result) == 2

    assert result[0].sensor_id == "DIGITRAFFIC:20002"
    assert result[0].timestamp == "2026-04-10T20:52:03Z"
    assert result[0].value == 312.0
    assert result[0].value_metadata["unit"] == "kpl/h"

    assert result[1].sensor_id == "DIGITRAFFIC:23001"
    assert result[1].timestamp == "2026-04-10T20:52:03Z"
    assert result[1].value == 32.0
    assert result[1].value_metadata["unit"] == "kpl/h"

def test_digitraffic_transform_empty():
    transformer = DigitrafficTransformer()

    result = transformer.transform([])

    assert result == []

def test_digitraffic_stddout_publisher(capsys):
    publisher = StdoutPublisher()

    publisher.publish(
        [
            Measurment(
                sensor_id="20002:5080",
                timestamp="2026-04-10T20:52:03Z",
                value=312.0,
                value_metadata={"unit": "kpl/h",
                                "time_window_start" : "2026-04-10T20:45:00Z",
                                "time_window_end" : "2026-04-10T20:50:00Z"},
            )
        ]
    )

    captured = capsys.readouterr()

    # parse output as JSON
    output = json.loads(captured.out.strip())

    assert output["sensor_id"] == "20002:5080"
    assert output["timestamp"] == "2026-04-10T20:52:03Z"
    assert output["value"] == 312.0
    assert output["value_metadata"]["unit"] == "kpl/h"
    assert output["value_metadata"]["time_window_start"] == "2026-04-10T20:45:00Z"
    assert output["value_metadata"]["time_window_end"] == "2026-04-10T20:50:00Z"
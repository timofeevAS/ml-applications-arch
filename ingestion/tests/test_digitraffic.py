import json

import pytest
from publisher.stdout import StdoutPublisher
from sources.digitraffic import DigitrafficSensorValue, DigitrafficSource, DigitrafficStationData
from transformers.base import Measurment
from transformers.digitraffic import DigitrafficTransformer

@pytest.mark.external
def test_digitraffic_fetch_smoke():
    source = DigitrafficSource()
    data = source.fetch()
    
    assert data.station_id == 20002
    assert len(data.sensor_values) > 0

def test_digitraffic_transform():
    transformer = DigitrafficTransformer()

    result = transformer.transform(DigitrafficStationData(
        station_id=20002, 
        sensor_values=[
            DigitrafficSensorValue(
                id=5016, 
                station_id=20002, 
                name='OHITUKSET_5MIN_KIINTEA_SUUNTA1', 
                short_name='kpl/h1', 
                time_window_start='2026-04-10T20:45:00Z',
                time_window_end='2026-04-10T20:50:00Z',
                measured_time='2026-04-10T20:52:03Z', 
                unit='kpl/h', 
                value=312.0
                ), 
            DigitrafficSensorValue(
                id=5080, 
                station_id=20002, 
                name='OHITUKSET_5MIN_KIINTEA_KAISTA3',
                short_name='mkk3',
                time_window_start='2026-04-10T20:45:00Z', 
                time_window_end='2026-04-10T20:50:00Z',
                measured_time='2026-04-10T20:52:03Z', 
                unit='kpl/h', 
                value=24.0
                )
            ]
        ))

    assert len(result) == 2

    assert result[0].sensor_id == "20002:5016"
    assert result[0].timestamp == "2026-04-10T20:52:03Z"
    assert result[0].value == 312.0
    assert result[0].value_metadata["unit"] == "kpl/h"
    assert result[0].value_metadata["time_window_start"] == "2026-04-10T20:45:00Z"
    assert result[0].value_metadata["time_window_end"] == "2026-04-10T20:50:00Z"

    assert result[1].sensor_id == "20002:5080"
    assert result[1].timestamp == "2026-04-10T20:52:03Z"
    assert result[1].value == 24.0
    assert result[1].value_metadata["unit"] == "kpl/h"
    assert result[1].value_metadata["time_window_start"] == "2026-04-10T20:45:00Z"
    assert result[1].value_metadata["time_window_end"] == "2026-04-10T20:50:00Z"

def test_digitraffic_transform_empty():
    transformer = DigitrafficTransformer()

    result = transformer.transform(
        DigitrafficStationData(station_id=20002, sensor_values=[])
    )

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
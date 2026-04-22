from __future__ import annotations
import json

import pytest
from publisher.stdout import StdoutPublisher
from sources.digitraffic import DigitrafficHistoryReplaySource, DigitrafficSource, DigitrafficTrafficFlowHourlySensor
from transformers.base import Measurment
from transformers.digitraffic import DigitrafficTransformer

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

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
    
    
def write_csv(path: Path, lines: list[str]) -> None:
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
def test_init_raises_when_csv_paths_empty() -> None:
    with pytest.raises(ValueError, match="csv_paths"):
        DigitrafficHistoryReplaySource(
            replay_start=datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc),
            csv_paths={},
        )


def test_parse_raw_line_returns_sensor(tmp_path: Path) -> None:
    csv_path = tmp_path / "station.csv"
    write_csv(csv_path, ["timestamp,value"])

    source = DigitrafficHistoryReplaySource(
        replay_start=datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc),
        csv_paths={1: csv_path},
    )

    event = source.parse_raw_line("2022-01-01T00:01:37+00:00,4", station_id=1)

    assert event == DigitrafficTrafficFlowHourlySensor(
        station_id=1,
        sensor_value=4,
        measured_time=datetime(2022, 1, 1, 0, 1, 37, tzinfo=timezone.utc),
        unit="veh/h",
    )


def test_fetch_returns_batch_for_single_station(tmp_path: Path) -> None:
    csv_path = tmp_path / "station.csv"
    write_csv(
        csv_path,
        [
            "timestamp,value",
            "2022-01-01T00:01:37+00:00,4",
        ],
    )

    replay_start = datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc)
    source = DigitrafficHistoryReplaySource(
        replay_start=replay_start,
        csv_paths={1: csv_path},
    )

    events = source.fetch()

    assert events == [
        DigitrafficTrafficFlowHourlySensor(
            station_id=1,
            sensor_value=4,
            measured_time=replay_start,
            unit="veh/h",
        )
    ]


def test_fetch_preserves_relative_time_offset_between_calls(tmp_path: Path) -> None:
    csv_path = tmp_path / "station.csv"
    write_csv(
        csv_path,
        [
            "timestamp,value",
            "2022-01-01T00:00:00+00:00,10",
            "2022-01-01T00:05:00+00:00,20",
        ],
    )

    replay_start = datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc)
    source = DigitrafficHistoryReplaySource(
        replay_start=replay_start,
        csv_paths={1: csv_path},
    )

    first_batch = source.fetch()
    second_batch = source.fetch()

    assert len(first_batch) == 1
    assert len(second_batch) == 1

    assert first_batch[0].measured_time == replay_start
    assert second_batch[0].measured_time == replay_start + timedelta(minutes=5)
    assert first_batch[0].sensor_value == 10
    assert second_batch[0].sensor_value == 20


def test_fetch_returns_events_from_all_stations_in_one_call(tmp_path: Path) -> None:
    csv_1 = tmp_path / "station_1.csv"
    csv_2 = tmp_path / "station_2.csv"

    write_csv(
        csv_1,
        [
            "timestamp,value",
            "2022-01-01T00:00:00+00:00,10",
            "2022-01-01T00:01:00+00:00,11",
        ],
    )
    write_csv(
        csv_2,
        [
            "timestamp,value",
            "2022-01-01T00:00:30+00:00,20",
            "2022-01-01T00:01:30+00:00,21",
        ],
    )

    replay_start = datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc)
    source = DigitrafficHistoryReplaySource(
        replay_start=replay_start,
        csv_paths={1: csv_1, 2: csv_2},
    )

    batch_1 = source.fetch()
    batch_2 = source.fetch()
    batch_3 = source.fetch()

    assert batch_1 == [
        DigitrafficTrafficFlowHourlySensor(
            station_id=1,
            sensor_value=10,
            measured_time=replay_start,
            unit="veh/h",
        ),
        DigitrafficTrafficFlowHourlySensor(
            station_id=2,
            sensor_value=20,
            measured_time=replay_start,
            unit="veh/h",
        ),
    ]

    assert batch_2 == [
        DigitrafficTrafficFlowHourlySensor(
            station_id=1,
            sensor_value=11,
            measured_time=replay_start + timedelta(minutes=1),
            unit="veh/h",
        ),
        DigitrafficTrafficFlowHourlySensor(
            station_id=2,
            sensor_value=21,
            measured_time=replay_start + timedelta(minutes=1),
            unit="veh/h",
        ),
    ]

    assert batch_3 == []


def test_fetch_skips_exhausted_station_and_returns_remaining_events(tmp_path: Path) -> None:
    csv_1 = tmp_path / "station_1.csv"
    csv_2 = tmp_path / "station_2.csv"

    write_csv(
        csv_1,
        [
            "timestamp,value",
            "2022-01-01T00:00:00+00:00,10",
        ],
    )
    write_csv(
        csv_2,
        [
            "timestamp,value",
            "2022-01-01T00:00:30+00:00,20",
            "2022-01-01T00:01:30+00:00,21",
        ],
    )

    source = DigitrafficHistoryReplaySource(
        replay_start=datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc),
        csv_paths={1: csv_1, 2: csv_2},
    )

    batch_1 = source.fetch()
    batch_2 = source.fetch()
    batch_3 = source.fetch()

    assert [event.station_id for event in batch_1] == [1, 2]
    assert [event.sensor_value for event in batch_1] == [10, 20]

    assert [event.station_id for event in batch_2] == [2]
    assert [event.sensor_value for event in batch_2] == [21]

    assert batch_3 == []
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


def test_fetch_returns_shifted_first_event(tmp_path: Path) -> None:
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

    event = source.fetch()

    assert event == DigitrafficTrafficFlowHourlySensor(
        station_id=1,
        sensor_value=4,
        measured_time=replay_start,
        unit="veh/h",
    )


def test_fetch_preserves_relative_time_offset(tmp_path: Path) -> None:
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

    first = source.fetch()
    second = source.fetch()

    assert first is not None
    assert second is not None
    assert first.measured_time == replay_start
    assert second.measured_time == replay_start + timedelta(minutes=5)
    assert first.sensor_value == 10
    assert second.sensor_value == 20


def test_fetch_round_robin_between_stations(tmp_path: Path) -> None:
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

    source = DigitrafficHistoryReplaySource(
        replay_start=datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc),
        csv_paths={1: csv_1, 2: csv_2},
    )

    e1 = source.fetch()
    e2 = source.fetch()
    e3 = source.fetch()
    e4 = source.fetch()
    e5 = source.fetch()

    assert e1 is not None and e1.station_id == 1 and e1.sensor_value == 10
    assert e2 is not None and e2.station_id == 2 and e2.sensor_value == 20
    assert e3 is not None and e3.station_id == 1 and e3.sensor_value == 11
    assert e4 is not None and e4.station_id == 2 and e4.sensor_value == 21
    assert e5 is None


def test_fetch_returns_none_when_all_files_exhausted(tmp_path: Path) -> None:
    csv_path = tmp_path / "station.csv"
    write_csv(
        csv_path,
        [
            "timestamp,value",
            "2022-01-01T00:01:37+00:00,4",
        ],
    )

    source = DigitrafficHistoryReplaySource(
        replay_start=datetime(2026, 4, 22, 12, 0, tzinfo=timezone.utc),
        csv_paths={1: csv_path},
    )

    assert source.fetch() is not None
    assert source.fetch() is None
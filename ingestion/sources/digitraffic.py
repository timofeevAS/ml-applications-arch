from dataclasses import dataclass
from pathlib import Path
import re
from typing import TextIO

import requests
from datetime import datetime

from sources.base import Source


@dataclass(slots=True)
class DigitrafficTrafficFlowHourlySensor:
    station_id: int
    sensor_value: int
    measured_time: datetime
    unit: str

class DigitrafficSource(Source):
    def __init__(self, station_ids: list[int]):
        super().__init__()
        self.station_ids = station_ids


    def fetch(self) -> list[DigitrafficTrafficFlowHourlySensor]:
        data: list[DigitrafficTrafficFlowHourlySensor] = []

        for station_id in self.station_ids:
            url = f"https://tie.digitraffic.fi/api/tms/v1/stations/{station_id}/data"
            raw_data = requests.get(url).json()
            
            # There is average number of vehicle per hour screening with '5-minute window'.
            pattern = re.compile(r"OHITUKSET_5MIN_KIINTEA_KAISTA\d+")

            # Gettings list of sensors which detect number of vehicle per lane.
            # For example:
            #   - per lane1: 10
            #   - per lane2: 33
            #   - per lane3: 3
            # total veh/h:   46
            sensor_values = [
                row
                for row in raw_data['sensorValues']
                if pattern.fullmatch(row['name'])
            ]

            hourly_flow = 0
            for sv in sensor_values:
                hourly_flow += sv["value"]
                
            data.append(DigitrafficTrafficFlowHourlySensor(
                station_id=station_id, 
                sensor_value=hourly_flow,
                measured_time=sensor_values[0]['measuredTime'],
                unit=sensor_values[0]['unit']))
        
        return data

@dataclass
class _ReplayFileState:
    station_id: int
    csv_path: Path
    file: TextIO | None = None
    header_skipped: bool = False
    base_timestamp: datetime | None = None
    last_offset: int = 0


@dataclass
class _ReplayFileState:
    station_id: int
    csv_path: Path
    file: TextIO | None = None
    header_skipped: bool = False
    base_timestamp: datetime | None = None
    last_offset: int = 0


class DigitrafficHistoryReplaySource(Source):
    """
    Replay historical Digitraffic data as if it were arriving in real time.

    Each station is backed by its own CSV file. The source reads files
    incrementally, keeps a separate file offset per station, and shifts
    original timestamps so that replay starts from ``replay_start``.
    """

    def __init__(self, replay_start: datetime, csv_paths: dict[int, Path]) -> None:
        super().__init__()

        if not csv_paths:
            raise ValueError("csv_paths must not be empty.")

        self.replay_start = replay_start
        self._states: dict[int, _ReplayFileState] = {}

        for station_id, csv_path in csv_paths.items():
            if not csv_path.exists():
                raise FileNotFoundError(csv_path)

            if csv_path.suffix.lower() != ".csv":
                raise ValueError(f"{csv_path} is not a .csv file.")

            self._states[station_id] = _ReplayFileState(
                station_id=station_id,
                csv_path=csv_path,
            )

        self._station_order = list(self._states.keys())
        self._next_station_idx = 0

    def parse_raw_line(
        self,
        line: str,
        station_id: int,
    ) -> DigitrafficTrafficFlowHourlySensor | None:
        """
        Parse one CSV line in format:
            timestamp,value
        Example:
            2022-01-01T00:01:37+00:00,4
        """
        try:
            ts_str, value_str = line.split(",", 1)
            return DigitrafficTrafficFlowHourlySensor(
                station_id=station_id,
                sensor_value=int(value_str),
                measured_time=datetime.fromisoformat(ts_str),
                unit="veh/h",
            )
        except (ValueError, TypeError):
            return None

    def _ensure_open(self, state: _ReplayFileState) -> TextIO:
        if state.file is None or state.file.closed:
            state.file = state.csv_path.open("r", encoding="utf-8", newline="")
            state.file.seek(state.last_offset)
        return state.file

    def close(self) -> None:
        for state in self._states.values():
            if state.file is not None and not state.file.closed:
                state.file.close()

    def _shift_timestamp(
        self,
        state: _ReplayFileState,
        original_ts: datetime,
    ) -> datetime:
        if state.base_timestamp is None:
            state.base_timestamp = original_ts

        delta = original_ts - state.base_timestamp
        return self.replay_start + delta

    def _fetch_from_state(
        self,
        state: _ReplayFileState,
    ) -> DigitrafficTrafficFlowHourlySensor | None:
        file = self._ensure_open(state)

        while True:
            line = file.readline()

            if line == "":
                state.last_offset = file.tell()
                return None

            state.last_offset = file.tell()

            if not state.header_skipped:
                state.header_skipped = True
                continue

            line = line.strip()
            if not line:
                continue

            event = self.parse_raw_line(line, station_id=state.station_id)
            if event is None:
                continue

            event.measured_time = self._shift_timestamp(state, event.measured_time)
            return event

    def fetch(self) -> list[DigitrafficTrafficFlowHourlySensor]:
        events: list[DigitrafficTrafficFlowHourlySensor] = []

        for station_id in self._station_order:
            state = self._states[station_id]
            event = self._fetch_from_state(state)
            if event is not None:
                events.append(event)

        return events
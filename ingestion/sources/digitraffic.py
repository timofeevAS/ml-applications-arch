from dataclasses import dataclass, field

import requests
from .base import Source

@dataclass(slots=True)
class DigitrafficSensorValue:
    id: int
    station_id: int
    name: str
    short_name: str | None
    time_window_start: str | None
    time_window_end: str | None
    measured_time: str | None
    unit: str | None
    value: float | int | None

@dataclass(slots=True)
class DigitrafficStationData:
    station_id: int
    sensor_values: list[DigitrafficSensorValue] = field(default_factory=list)

class DigitrafficSource(Source):
    SENSORS_ID = [5016, 5080]
    STATION_ID = 20002
    URL = f"https://tie.digitraffic.fi/api/tms/v1/stations/{STATION_ID}/data"

    def fetch(self) -> DigitrafficStationData:
        raw_data = requests.get(self.URL).json()
        
        sensor_values = [
            row
            for row in raw_data['sensorValues']
            if row['id'] in self.SENSORS_ID
            ]
            
        data = DigitrafficStationData(station_id=self.STATION_ID,
                                      sensor_values=self._parse_sensor_values(sensor_values))
        
        return data
    
    def _parse_sensor_values(self, sensor_values: list) -> list[DigitrafficSensorValue]:
        values = [
            DigitrafficSensorValue(
                id=row["id"],
                station_id=row["stationId"],
                name=row["name"],
                short_name=row.get("shortName"),
                time_window_start=row.get("timeWindowStart"),
                time_window_end=row.get("timeWindowEnd"),
                measured_time=row.get("measuredTime"),
                unit=row.get("unit"),
                value=row.get("value"),
            )
            for row in sensor_values
        ]

        return values
from dataclasses import dataclass, field
import re

import requests
from .base import Source

@dataclass(slots=True)
class DigitrafficTrafficFlowHourlySensor:
    station_id: int
    sensor_value: int
    measured_time: str # TODO: datetime?
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
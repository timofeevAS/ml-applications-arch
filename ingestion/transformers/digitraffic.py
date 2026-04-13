from sources.digitraffic import DigitrafficStationData
from transformers.base import Measurment, Transformer


class DigitrafficTransformer(Transformer):
    def transform(self, digitraffic_data: DigitrafficStationData) -> list[Measurment]:
        result: list[Measurment] = []
        for sv in digitraffic_data.sensor_values:
            measurment = Measurment(
                sensor_id=f"{digitraffic_data.station_id}:{sv.id}",
                timestamp=sv.measured_time,
                value=sv.value,
                value_metadata = {
                    "unit" : sv.unit,
                    "time_window_start" : sv.time_window_start,
                    "time_window_end" : sv.time_window_end
                    }
                )
            
            result.append(measurment)
        
        return result
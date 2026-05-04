from sources.digitraffic import DigitrafficTrafficFlowHourlySensor

from transformers.base import Measurment, Transformer


class DigitrafficTransformer(Transformer):
    def transform(self, digitraffic_data: list[DigitrafficTrafficFlowHourlySensor]) -> list[Measurment]:
        result: list[Measurment] = []
        for sv in digitraffic_data:
            measurment = Measurment(
                sensor_id=f"DIGITRAFFIC:{sv.station_id}",
                timestamp=sv.measured_time,
                value=sv.sensor_value,
                value_metadata = {
                    "unit" : sv.unit
                    }
                )

            result.append(measurment)

        return result

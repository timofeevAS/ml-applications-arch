import pytest
from sources.digitraffic import DigitrafficSource


def test_digitraffic_fetch_smoke():
    source = DigitrafficSource()
    data = source.fetch()
    
    assert data.station_id == 20002
    assert len(data.sensor_values) > 0
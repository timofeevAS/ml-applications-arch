from pydantic import BaseModel


class SensorResponse(BaseModel):
    """
    id      номер датчика
    name    название для интерфейса
    metric  колонка из CSV, которую этот датчик измеряет
    unit    единица измерения
    """
    id: int
    name: str
    metric: str
    unit: str | None = None


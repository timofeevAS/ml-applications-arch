from pydantic import BaseModel

'''
id      — номер датчика
name    — название для интерфейса
metric  — колонка из CSV, которую этот датчик измеряет
unit    — единица измерения
'''

class SensorResponse(BaseModel):
    id: int
    name: str
    metric: str
    unit: str | None = None


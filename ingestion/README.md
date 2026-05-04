# Ingestion: Project description
## Ingestion layer
Сервис который занимается сбором сырых данных и их представлением в унифицированном формате и передачей на следующие слои:
```
                        [Sensors]
                            |
                            |
                            ↓
                [Source data collector]
                            |
                            |
                            ↓
                      [Generalize]
                            |
                            |
                            ↓
                      [Publishing]
                            |
                            |
                            ↓
                     [Next layers...]
```
Выше представлена примерная схема порядка обработки данных с датчиков.

Обобщенным предсталвением является структура:
```python
@dataclass(slots=True)
class Measurment:
    sensor_id: str
    timestamp: str
    value: float | int | None
    value_metadata: dict[str, Any] = field(default_factory=dict)
```
В таком виде данные могут быть переданы в хранилище, брокеру сообщений, выведены в консоль.

## How to run?
Для запуска сервиса необходимо выполнить следующие шаги:
```bash
python -m venv .venv
# активировать окружение
pip install -r requirements.txt
# создать файл .env по примеру из .env.example
python main.py
# сервис запущен
```
# Использование скрипта analize.py

## Обязательные флаги
1. --url <маршрут запроса>
2. --m <модель>
2. --t <температура>
4. --req <источник запросов в виде .csv с колонками id и request>
5. --res <файл вывода сводной таблицы с колонками id, request, response>

## Пример использования
```
py .\analize.py --url http://127.0.0.1:8080/v1/chat/completions --m qwen2.5:7b --t -0.5 --req .\requests.csv --res .\table.csv
```
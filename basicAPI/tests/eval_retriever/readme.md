# Формирование данных 

## Условия вызова
Перед запуском директория должна содержать:
- <номер попытки>/data/recipes или <номер попытки>/data/sqlite_test.db - источник документов
- <номер попытки>/data/queries - тестовые запросы в виде массива JSON

Пример запуска:
```
py -m tests.eval_retriever.recieve_answers --path "tests/eval_retriever" --at 1
```
# Оценка результатов
Перед запуском директория должна содержать:
- <номер попытки>/qrels.json - Qrels файл JSON-формата
- <номер попытки>/runs.json - Результаты запуска
- <номер попытки>/settings.json - Настройки запуска

Пример запуска:
```
py -m tests.eval_retriever.eval --path "tests/eval_retriever" --at 1
```
# Тестирование агента

## 1. Формирование данных для оценки get_test_values.py
### Условия вызова
Необходим файл JSON формата с массивом запросов, расположенный по умолчанию в /tests/eval_agent/queries.json
```
[
    {"query": "Как приготовить борщ?", "scenario": 1},
    {"query": "Как приготовить лобстера" , "scenario": 2}
]
```
### Вызов
```
py -m tests.eval_agent.get_test_values
```
### Дополнительные параметры
```
py -m tests.agent_is_working.test 
    --inp <файл с запросами> 
    --out <вывод результатов> 
    --tries <число прогонов> 
    --sleep <пауза между запросами в сек> 
    --m <модель>
```

## 2. Подсчет метрик eval.py
### Условия вызова
Необходим файл c ранее посчитанными метриками /tests/eval_agent/results.json
### Вызов
```
py -m tests.eval_agent.eval
```
### Дополнительные параметры
```
py -m tests.agent_is_working.test 
    --val <файл с оценками> 
    --out <вывод результатов> 
```
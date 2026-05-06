# Формирование набора данных

## 1. generate_dataset - Генерация данных 
### Условия вызова
1. Необходим JSON-файл с настройками генерации
```
[
    {
        "name": "string",
        "prompt": "string",
        "injections": [
            {"placeholder": "string", "value": "string"},
        ]
    }
]
```
2. Необходим JSON-файл с данными для доступа к модели
```
{
    "url": "string",
    "key": "string"
}
```
### Шаблон вызова
```
py ./generate_dataset.py 
    --settings <путь к JSON с настройками> 
    --env <путь к JSON с данными для доступа к модели> 
    --output <csv-файл вывода> 
    --m <модель> 
    --t <температура>
```

## 2. count - Подсчет структуры данных
### Условия вызова
Необходим файл вывода - результат вызова предыдущей процедуры
```
id,combo,query
number,"string","string"
```
### Шаблон вызова
```
py .\count.py 
    --data <csv-файл с данными> 
    --output <csv-файл вывода>
```
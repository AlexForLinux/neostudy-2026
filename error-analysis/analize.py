import argparse
import os
import sys
import csv
import urllib.request
import json

def send_request(id, request, url, model, temperature):
    data = {
        'model': model,
        'temperature': temperature,
        'messages': [
            {
                'role': 'system',
                'content': 'Ты - опытный кулинар, который что только ни готовил в своей жизни. Помогай людям искать идеальные для них рецепты, давай адекватные безопасные советы. Будь отзывчивым и дружелюбным'
            },
            {
                'role': 'user',
                'content': request
            }
        ]
    }
    data_bytes = json.dumps(data).encode('utf-8')

    req = urllib.request.Request(url, data = data_bytes, method='POST')
    req.add_header('Content-Type', 'application/json')

    try:
        with urllib.request.urlopen(req) as response:
            res = json.loads(response.read().decode('utf-8'))
            return res['message']['content']
        
    except Exception as e:
        print(f"[ERROR] Request #{id} - {e}")
        sys.exit(1)
    
def iterate(req, res, url, model, temperature):

    try:
        with open(req, 'r', encoding='utf-8') as s:
            reader = csv.DictReader(
                s,
                fieldnames=['id', 'request'],
                quoting=csv.QUOTE_ALL,
                quotechar='"',
                escapechar='\\'
            )
            next(reader) #skip headers
            
            with open(res, 'w', encoding='utf-8', newline='') as t:
                writer = csv.DictWriter(
                    t, 
                    fieldnames=['id', 'request', 'response'],
                    quoting=csv.QUOTE_ALL,
                    quotechar='"',
                    escapechar='\\'
                )
                writer.writeheader()

                for row in reader:
                    print(f"[INFO] Sending Request #{row['id']}")
                    writer.writerow({
                        'id': row['id'],
                        'request': row['request'],
                        'response': send_request(row['id'], row['request'], url, model, temperature)
                    })

    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)
    
def main():
    parser = argparse.ArgumentParser(
        description='Процесс итеративного анализа',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--url',
        type=str,
        required=True,
        help='Маршрут до AI-системы'
    )
    
    parser.add_argument(
        '--req',
        type=str,
        required=True,
        help='Файл запросов .csv'
    )

    parser.add_argument(
        '--res',
        type=str,
        required=True,
        help='Сводный файл запросов ответов .csv'
    )

    parser.add_argument(
        '--m',
        type=str,
        required=True,
        help='Модель'
    )

    parser.add_argument(
        '--t',
        type=float,
        required=True,
        help='Температура'
    )

    args = parser.parse_args()
    
    if not os.path.exists(args.req):
        print(f"[ERROR] Входной файл не существует!")
        sys.exit(1)

    if os.path.exists(args.res):
        print(f"[ERROR] Выходной файл уже существует")
        sys.exit(1)
    
    if not os.path.isfile(args.req):
        print(f"[ERROR] '{args.req}' не является файлом!")
        sys.exit(1)

    iterate(args.req, args.res, args.url, args.m, args.t)

if __name__ == "__main__":
    main()
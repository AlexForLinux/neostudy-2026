import argparse
import os
import sys
import json
from openai import OpenAI
import pandas as pd
from pydantic import BaseModel, Field
from typing import List, Annotated

class QueriesArray(BaseModel):
    queries: Annotated[List[str], Field(
        default_factory=list,
        description="user queries"
    )]

def generate(set_path, env, model, temperature):

    with open(env, 'r', encoding='utf-8') as f:
        env_dict = json.load(f)

        api_url = env_dict['url']
        api_key = env_dict['key']

        client = OpenAI(
            base_url=api_url,
            api_key=api_key
        )
    
    with open(set_path, 'r', encoding='utf-8') as f:
        set_dict = json.load(f)

        id = 0
        final_df = pd.DataFrame(columns=["id", "combo", "query"])

        for set_ in set_dict:
            combo = set_['name']
            prompt = None
            prompt_path = set_['prompt_path']
            injections = set_['injections']

            with open(prompt_path, 'r', encoding='utf-8') as pf:
                prompt = pf.read()

            for injection in injections:
                placeholder = injection['placeholder']
                value = injection['value']
                prompt = prompt.replace(placeholder, str(value))

            print(f"[INFO] Generating {combo}")

            response = client.chat.completions.parse(
                model = model,
                temperature=temperature,
                messages = [{
                    'role': 'user',
                    'content': prompt
                }],
                response_format=QueriesArray
            )

            queries_json = response.choices[0].message.parsed
            queries = queries_json.queries

            df = pd.DataFrame(queries, columns=['query'])
            df["combo"] = combo
            df["id"] = range(id, id + len(df))
            df = df[["id", "combo", "query"]]
            final_df = pd.concat([final_df, df], ignore_index=True)

            id += len(df)

        return final_df

def main():
    parser = argparse.ArgumentParser(
        description='Генерация данных',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--settings',
        type=str,
        required=True,
        help='Файл настроек JSON'
    )

    parser.add_argument(
        '--env',
        type=str,
        required=True,
        help='Файл настроек JSON'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Файл вывода запросов'
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
    
    if not os.path.exists(args.settings):
        print(f"[ERROR] Файл настроек не существует!")
        sys.exit(1)

    if not os.path.exists(args.env):
        print(f"[ERROR] Файл конфигурации не существует!")
        sys.exit(1)

    if os.path.exists(args.output):
        print(f"[ERROR] Файл вывода уже существует!")
        sys.exit(1)

    try:
        result_df = generate(args.settings, args.env, args.m, args.t)
        result_df.to_csv(args.output, index=False)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
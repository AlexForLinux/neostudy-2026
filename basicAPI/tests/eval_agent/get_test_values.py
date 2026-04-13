import os
import sys
import json
import argparse
import time
from app.config import settings
from app.services.prompt_service import PromptService
from app.services.recipe_retriever_service import RecipeRetrieverService
from app.repo.recipe_repo import RecipeRepo
from app.services.agentic_service import AgenticService
from sentence_transformers import SentenceTransformer

def test_runs(inp, out, tries, sleep, model):

    prompt_service = PromptService({
        'recipe': settings.recipe_prompt,
        'advice': settings.advice_prompt,
        'other': settings.other_prompt,
        'collect_recipe': settings.collect_recipe,
        'build_recipe': settings.build_recipe
    })

    recipeRepo = RecipeRepo(settings.sqlite_db, settings.recipe_docs)
    recipe_retriever_service = RecipeRetrieverService(
        settings.recipe_faiss,
        SentenceTransformer("BAAI/bge-m3"),
        recipeRepo
    )

    agentic_service = AgenticService(recipe_retriever_service, prompt_service)

    if  (tries < 1):
        print(f"[ERROR] Invalid 'tries' value")
        sys.exit(1)

    if  (sleep < 0):
        print(f"[ERROR] Invalid 'sleep' value")
        sys.exit(1)
    
    if  (not os.path.exists(inp)):
        print(f"[ERROR] Input file {inp} does not exist")
        sys.exit(1)

    if  (os.path.exists(out)):
        print(f"[ERROR] Output file {out} already exists")
        sys.exit(1)

    results = []

    print('[INFO] Start testing')
    with open(inp, "r", encoding="utf-8") as qf:
        queries = json.load(qf)

        for q in queries:

            query = q['query']
            scenario = q['scenario']
            values = []

            for i in range(tries):

                if (sleep):
                    print(f"[INFO] Pause for {sleep} sec")
                    time.sleep(sleep)

                print(f"[INFO] Test query '{query}' - {i+1}/{tries}")

                start = time.perf_counter()
                response = agentic_service.run(model, query)
                end = time.perf_counter()

                values.append({
                    "try": i,
                    "steps": response["steps"],
                    "total_time": end - start,
                    "tool_calling": response["tool_calling"],
                    "scenario_match": None,  #выставляется отдельно
                    "response": response["response"].model_dump(),
                    "response_quality": None, #выставляется отдельно
                })

            res = {
                'query': query,
                'scenario': scenario,
                'values': values
            }

            print(res)

            results.append(res)

        print(f"[INFO] Finished successfully")

    with open(out, "w", encoding="utf-8") as wf:
        json.dump(results, wf, ensure_ascii=False, indent=4)

def main():
    parser = argparse.ArgumentParser(
        description='Формирование набора данных для оценки агента',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--inp',
        type=str,
        required=False,
        help='JSON-file with queries',
        default='tests/eval_agent/queries.json'
    )

    parser.add_argument(
        '--out',
        type=str,
        required=False,
        help='Output file',
        default='tests/eval_agent/results.json'
    )

    parser.add_argument(
        '--tries',
        type=int,
        required=False,
        help='Number of tries',
        default=3
    )

    parser.add_argument(
        '--sleep',
        type=int,
        required=False,
        help='Pause between tries in seconds',
        default=60
    )

    parser.add_argument(
        '--m',
        type=str,
        required=False,
        help='Model',
        default='gpt-oss-120b'
    )

    args = parser.parse_args()

    try:
        test_runs(args.inp, args.out, args.tries, args.sleep, args.m)
    except Exception as e:
        print(f'[ERROR] {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
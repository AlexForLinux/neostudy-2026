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
import numpy as np

def eval_metrix(inp, out):

    if  (not os.path.exists(inp)):
        print(f"[ERROR] Input file {inp} does not exist")
        sys.exit(1)

    if  (os.path.exists(out)):
        print(f"[ERROR] Output file {out} already exists")
        sys.exit(1)

    with open(inp, "r", encoding="utf-8") as vf:
        data = json.load(vf)

        target = ['steps', 'total_time', 'scenario_match', 'response_quality']

        by_scenario = {
            "all": dict(),
            1: dict(),
            2: dict(),
        }

        by_queries = []

        for query_res in data:
            query = query_res['query']
            scenario = query_res['scenario']
            values = query_res['values']

            q_metrix = dict()

            for value_dict in values:

                for key in target:

                    if q_metrix.get(key, None) is None:
                        q_metrix[key] = []

                    val = value_dict[key]
                    if val is None:
                        val = 0
                        print(f"[WARN] Missing value {key} in {query}. Set 0")

                    q_metrix[key].append(val)

            by_queries.append({
                "query": query,
                "result": q_metrix
            })

            for key in target:
                if by_scenario[scenario].get(key, None) is None:
                    by_scenario[scenario][key] = []
                    by_scenario["all"][key] = []

                by_scenario[scenario][key].extend(q_metrix[key])
                by_scenario["all"][key].extend(q_metrix[key])

        query_result = []
        for q_metrix in by_queries:
            query_result.append({
                "query": q_metrix['query'],
                "result": { k: {"avg": np.mean(v), "std": np.std(v)} for k,v in q_metrix['result'].items()}
            })

        scenario_1 = {
            k: {"avg": np.mean(v), "std": np.std(v)} for k,v in by_scenario[1].items()
        }
        scenario_2 = {
            k: {"avg": np.mean(v), "std": np.std(v)} for k,v in by_scenario[2].items()
        }
        all = {
            k: {"avg": np.mean(v), "std": np.std(v)} for k,v in by_scenario["all"].items()
        }

    answer = {
        "all": all,
        "scenario-1": scenario_1,
        "scenario-2": scenario_2,
        "queries": query_result
    }

    with open(out, "w", encoding="utf-8") as wf:
        json.dump(answer, wf, ensure_ascii=False, indent=4)

def main():
    parser = argparse.ArgumentParser(
        description='Формирование набора данных для оценки агента',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--val',
        type=str,
        required=False,
        help='JSON-file with result values of agent evaluation',
        default='tests/eval_agent/results.json'
    )

    parser.add_argument(
        '--out',
        type=str,
        required=False,
        help='File to write evaluation results',
        default='tests/eval_agent/evals.json'
    )

    args = parser.parse_args()

    try:
        eval_metrix(args.val, args.out)
    except Exception as e:
        print(f'[ERROR] {e}')
        sys.exit(1)

if __name__ == "__main__":
    main()
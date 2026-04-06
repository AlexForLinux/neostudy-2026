import argparse
from app.services.recipe_retriever_service import RecipeRetrieverService
from app.repo.recipe_repo import RecipeRepo
from sentence_transformers import SentenceTransformer
import json
import os
import sys

def recieve(test_forlder='tests/eval_retriever', attempt=1):
    test_attempt = os.path.join(test_forlder, str(attempt))

    qrels_path = os.path.join(test_attempt, 'qrels.json')
    runs_path = os.path.join(test_attempt, 'runs.json')
    settings_path = os.path.join(test_attempt, 'settings.json')

    if os.path.exists(qrels_path) or os.path.exists(runs_path) or os.path.exists(settings_path):
        print('[ERROR] Results exists')
        sys.exit(1)

    data_path = os.path.join(test_attempt, 'data')

    queries_path = os.path.join(data_path, 'queries.json')
    corpus_path = os.path.join(data_path, 'recipes')
    sqlite_path = os.path.join(data_path, 'sqlite_test.db')
    faiss_path = os.path.join(data_path, 'faiss_test.db')

    if not os.path.exists(queries_path):
        print('[ERROR] Queries are not presented')
        sys.exit(1)

    if not os.path.exists(corpus_path) and not os.path.exists(sqlite_path):
        print('[ERROR] Source of recipies is not presented')
        sys.exit(1)

    settings = {
        'corpus': corpus_path,
        'db': sqlite_path,
        'faiss': faiss_path,
        'queries': queries_path,
        'embed_model': "BAAI/bge-m3",
        'k': 3
    }

    embed_model = SentenceTransformer(settings['embed_model'])
    db = RecipeRepo(settings['db'], settings['corpus'])
    service = RecipeRetrieverService(settings['faiss'], embed_model, db)

    with open(settings_path, "w", encoding="utf-8") as sf:
        json.dump(settings, sf, ensure_ascii=False,indent=4)
        print(f"[INFO] Settings apllied")

    with open(settings['queries'], "r", encoding="utf-8") as qf:
        queries = json.load(qf)

        runs = []
        qrels = []

        for query in queries:
            print(f"[INFO] Processing query #{query['qid']}")

            topK = service.retrieve(query['query'], settings['k'])

            for rank, data in enumerate(topK):

                rid, score, doc = data

                runs.append({
                    "q_id": query['qid'],
                    "r_id": rid,
                    "score": score,
                    "rank": rank + 1,
                })

                qrels.append({
                    "q_id": query['qid'],
                    "r_id": rid,
                    "score": None, # выставляется отдельно при определении релевантности
                })

        with open(runs_path, "w", encoding="utf-8") as rf:
            json.dump(runs, rf, ensure_ascii=False, indent=4)

        with open(qrels_path, "w", encoding="utf-8") as qf:
            json.dump(qrels, qf, ensure_ascii=False, indent=4)
        

def main():
    parser = argparse.ArgumentParser(
        description='Формирование набора данных',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--path',
        type=str,
        required=True,
        help='Маршрут до директории'
    )
    
    parser.add_argument(
        '--at',
        type=int,
        required=True,
        help='Попытка'
    )

    args = parser.parse_args()

    recieve(args.path, args.at)

if __name__ == "__main__":
    main()
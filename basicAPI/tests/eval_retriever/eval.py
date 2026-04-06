import argparse
import os
import json
import numpy as np

def calc_mrr_k(qrels_dict, runs_dict):
    reversed_ranks = dict()

    for run_key, run in runs_dict.items():
        q_id, r_id = run_key
        qrel = qrels_dict[run_key]

        q_score = qrel['score']
        r_rank = run['rank']

        if q_score is None:
            print(f'[WARN] Skipped score for q_id={q_id}, r_id={r_id}. Set 0')
            q_score = 0

        if reversed_ranks.get(q_id, None) is None:
            reversed_ranks[q_id] = 0

        rv = q_score / r_rank
        if (rv > reversed_ranks[q_id]): #ранг у самого первого релеватного наибольший
            reversed_ranks[q_id] = rv

    mrr_k = np.mean(list(reversed_ranks.values()))
    return float(mrr_k)

def calc_map_k(qrels_dict, runs_dict, k):

    relevance = dict()

    for run_key, run in runs_dict.items():
        q_id, r_id = run_key
        qrel = qrels_dict[run_key]

        q_score = qrel['score']
        r_rank = run['rank']

        if q_score is None:
            print(f'[WARN] Skipped score for q_id={q_id}, r_id={r_id}. Set 0')
            q_score = 0

        if relevance.get(q_id, None) is None:
            relevance[q_id] = [0] * k #массив релевантности в k-выборке

        relevance[q_id][r_rank - 1] = q_score

    ap_sum = 0
    rel_items = relevance.items()
    for q_id, rel_arr in rel_items:

        tp = 0
        fp = 0
        precision_mult_rel_sum = 0

        for rel in rel_arr:
            if rel == 0:
                fp += 1
                # precision_mult_rel += tp / (tp + fp) * 0 <=> precision_mult_rel += 0 <=> ничего
            else:
                tp += 1
                precision_mult_rel_sum += tp / (tp + fp)

        if tp != 0:
            ap_sum += precision_mult_rel_sum / tp

    return float(ap_sum / len(rel_items))

def eval(test_forlder='tests/eval_retriever', attempt=1):
    TEST_ATTEMPT = os.path.join(test_forlder, str(attempt))
    QRELS_FILE = os.path.join(TEST_ATTEMPT, 'qrels.json')
    RUN_FILE = os.path.join(TEST_ATTEMPT, 'runs.json')
    SETTINGS_FILE = os.path.join(TEST_ATTEMPT, 'settings.json')

    with open(SETTINGS_FILE, "r", encoding="utf-8") as sf:
        settngs = json.load(sf)

        with open(RUN_FILE, "r", encoding="utf-8") as rf:
            runs = json.load(rf)
            runs_dict = {
                (run['q_id'], run['r_id']): {"score": run['score'], "rank": run["rank"]} 
                for run in runs
            }

            K = settngs['k']

            with open(QRELS_FILE, "r", encoding="utf-8") as qf:
                qrels = json.load(qf)
                qrels_dict = {
                    (qrel['q_id'], qrel['r_id']): {"score": qrel['score']} 
                    for qrel in qrels
                }

                result = {
                    f'MRR@{K}': calc_mrr_k(qrels_dict, runs_dict),
                    f'mAP@{K}': calc_map_k(qrels_dict, runs_dict, K)
                }
                
                return result


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

    res = eval(args.path, args.at)
    print(res)

if __name__ == "__main__":
    main()
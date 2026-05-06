import argparse
import os
import sys
import pandas as pd

def count(out_path):
    out_df = pd.read_csv(out_path)
    res_df = out_df.groupby('combo').size().reset_index(name='count')
    return res_df

def main():
    parser = argparse.ArgumentParser(
        description='Оценка структуры датасета',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--data',
        type=str,
        required=True,
        help='Набор данных в виде csv (id, combo, query)'
    )

    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Файл вывода результатов'
    )
    
    args = parser.parse_args()
    
    if not os.path.exists(args.data):
        print(f"[ERROR] Файл данных не существует!")
        sys.exit(1)

    if os.path.exists(args.output):
        print(f"[ERROR] Файл вывода результатов уже существует!")
        sys.exit(1)

    try:
        result_df = count(args.data)
        result_df.to_csv(args.output, index=False)
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
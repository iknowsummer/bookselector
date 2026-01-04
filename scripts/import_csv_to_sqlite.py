import pandas as pd
import sqlite3
import os

dir_base = os.path.dirname(__file__)
CSV_PATH = os.path.join(dir_base, "../datafile/sample-books.csv")
DB_PATH = os.path.join(dir_base, "..", "data", "sqlite.db")
TABLE_NAME = "books"


def read_csv_to_df(csv_path):
    df = pd.read_csv(csv_path, encoding="utf-8", dtype={"isbn": str})
    print(f"CSVカラム名: {df.columns.tolist()}")
    return df


def insert_df_to_db(df, db_path, table_name):
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    columns = df.columns.tolist()
    placeholders = ", ".join(["?"] * len(columns))
    sql = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    for _, row in df.iterrows():
        values = [row.get(col, "") for col in columns]
        if not values[0]:
            print(f"{columns[0]}が空です。row: {row}")
        cur.execute(sql, values)
    conn.commit()
    conn.close()
    print("DBへのインポートが完了しました。")


def main():
    db_dir = os.path.dirname(DB_PATH)
    if not os.path.exists(db_dir):
        print(f"DBディレクトリが存在しません: {db_dir}")
        return
    if not os.path.exists(DB_PATH):
        print(f"DBファイルが存在しません: {DB_PATH}")
        return
    df = read_csv_to_df(CSV_PATH)
    insert_df_to_db(df, DB_PATH, TABLE_NAME)


if __name__ == "__main__":
    main()

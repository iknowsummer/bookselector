import sqlite3

# 設定
DB_PATH = "backend/app/sqlite.db"
TABLE_NAME = "books"

# 動作フラグ
DROP_TABLE = False  # True: テーブルごと削除, False: 中身だけ削除


def main():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        if DROP_TABLE:
            cursor.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
            print(f"テーブル '{TABLE_NAME}' を削除しました。")
        else:
            cursor.execute(f"DELETE FROM {TABLE_NAME}")
            print(f"テーブル '{TABLE_NAME}' の中身を全削除しました。")
        conn.commit()
    except Exception as e:
        print("エラー:", e)
    finally:
        conn.close()


if __name__ == "__main__":
    main()

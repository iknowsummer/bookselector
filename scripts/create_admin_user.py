import sqlite3
from datetime import datetime

# 設定
DB_PATH = "backend/sqlite.db"


def main():
    """adminユーザーを作成するマイグレーションスクリプト"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # users テーブルの存在確認
        cursor.execute("""
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='users'
        """)

        if not cursor.fetchone():
            print("エラー: usersテーブルが存在しません。")
            print("先にアプリケーションを起動してテーブルを作成してください。")
            return

        # admin ユーザーが既に存在するか確認
        cursor.execute("SELECT id FROM users WHERE name = ?", ("admin",))
        if cursor.fetchone():
            print("adminユーザーは既に存在します。")
            return

        # admin ユーザーを挿入（既存のBooksテーブルと同じ形式に揃える）
        cursor.execute(
            "INSERT INTO users (name, created_at) VALUES (?, ?)",
            ("admin", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        )
        conn.commit()

        # 作成されたユーザーを取得
        cursor.execute("SELECT id, name, created_at FROM users WHERE name = ?", ("admin",))
        user = cursor.fetchone()

        print(f"adminユーザーを作成しました:")
        print(f"  ID: {user[0]}")
        print(f"  Name: {user[1]}")
        print(f"  Created: {user[2]}")

    except Exception as e:
        conn.rollback()
        print(f"エラーが発生しました: {e}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

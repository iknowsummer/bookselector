"""
マルチユーザー対応データベース移行スクリプト

このスクリプトは以下の処理を実行します:
1. データベースのバックアップ作成
2. users テーブルと admin ユーザーの存在確認
3. user_books 中間テーブルの作成
4. books テーブルから user_books へのデータ移行 (note, status, shelf_id)
5. books テーブルの再作成（ユーザー固有カラムを削除）
6. データ整合性の検証

使用方法:
    python scripts/migrate_to_multiuser.py
"""

import sqlite3
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Windows環境でのUnicodeエラーを回避
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')


def backup_database(db_path: str) -> str:
    """
    タイムスタンプ付きバックアップを作成

    Args:
        db_path: データベースファイルのパス

    Returns:
        バックアップファイルのパス
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backend/sqlite_backup_{timestamp}.db"

    shutil.copy2(db_path, backup_path)
    print(f"✓ バックアップ作成: {backup_path}")

    return backup_path


def verify_users_table(conn: sqlite3.Connection):
    """
    users テーブルと admin ユーザーの存在を確認

    Args:
        conn: データベース接続

    Raises:
        ValueError: users テーブルまたは admin ユーザーが存在しない場合
    """
    cursor = conn.cursor()

    # users テーブルの存在確認
    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name='users'
    """)
    if not cursor.fetchone():
        raise ValueError("users テーブルが存在しません")

    # admin ユーザーの存在確認
    cursor.execute("SELECT id, name FROM users WHERE id = 1")
    admin_user = cursor.fetchone()
    if not admin_user:
        raise ValueError("管理ユーザー (id=1) が存在しません")

    print(f"✓ users テーブル確認: OK")
    print(f"✓ 管理ユーザー確認: id={admin_user[0]}, name={admin_user[1]}")


def create_user_books_table(conn: sqlite3.Connection):
    """
    user_books テーブルとインデックスを作成

    Args:
        conn: データベース接続
    """
    cursor = conn.cursor()

    # user_books テーブル作成
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            book_id INTEGER NOT NULL,
            note TEXT,
            status VARCHAR(20) DEFAULT 'unread' NOT NULL,
            shelf_id INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
            FOREIGN KEY (shelf_id) REFERENCES shelves(id) ON DELETE SET NULL,
            UNIQUE (user_id, book_id)
        )
    """)

    # インデックス作成
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_books_user_id ON user_books(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_books_book_id ON user_books(book_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_books_status ON user_books(status)")
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_user_books_shelf_id ON user_books(shelf_id)")

    print("✓ user_books テーブル作成: OK")


def migrate_book_data(conn: sqlite3.Connection):
    """
    note, status, shelf_id を user_books へ移行

    既存の全書籍を管理ユーザー (id=1) に紐付けます。

    Args:
        conn: データベース接続
    """
    cursor = conn.cursor()

    # 既存の books データを user_books へコピー
    cursor.execute("""
        INSERT INTO user_books (user_id, book_id, note, status, shelf_id, created_at, updated_at)
        SELECT
            1 as user_id,
            id as book_id,
            note,
            status,
            shelf_id,
            created_at,
            created_at as updated_at
        FROM books
    """)

    migrated_count = cursor.rowcount
    print(f"✓ データ移行: {migrated_count} 件の書籍を user_books へ移行")


def migrate_books_table(conn: sqlite3.Connection):
    """
    books テーブルからユーザー固有カラムを削除

    新しい books テーブルを作成し、ユーザー固有カラム (note, status, shelf_id) を除外します。

    Args:
        conn: データベース接続
    """
    cursor = conn.cursor()

    # 新しい books テーブルを作成
    cursor.execute("""
        CREATE TABLE books_new (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            author VARCHAR(200),
            description TEXT,
            target_age VARCHAR(50),
            isbn VARCHAR(13) UNIQUE,
            image_url VARCHAR(500),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP NOT NULL
        )
    """)

    # インデックス作成
    cursor.execute("CREATE INDEX IF NOT EXISTS ix_books_created_at ON books_new(created_at)")

    # データ移行（note, status, shelf_id を除外）
    cursor.execute("""
        INSERT INTO books_new (id, title, author, description, target_age, isbn, image_url, created_at)
        SELECT id, title, author, description, target_age, isbn, image_url, created_at
        FROM books
    """)

    migrated_count = cursor.rowcount

    # 旧テーブルを削除し、新テーブルをリネーム
    # 注: SQLiteはデフォルトで外部キー制約が無効なので、DROP TABLE しても user_books は削除されない
    cursor.execute("DROP TABLE books")
    cursor.execute("ALTER TABLE books_new RENAME TO books")

    print(f"✓ books テーブル更新: {migrated_count} 件の書籍データを移行（ユーザー固有カラム削除）")


def verify_migration(conn: sqlite3.Connection):
    """
    データ整合性を検証

    Args:
        conn: データベース接続

    Raises:
        ValueError: データ整合性チェックに失敗した場合
    """
    cursor = conn.cursor()

    # books テーブルの書籍数をカウント
    cursor.execute("SELECT COUNT(*) FROM books")
    books_count = cursor.fetchone()[0]

    # 管理ユーザーの user_books をカウント
    cursor.execute("SELECT COUNT(*) FROM user_books WHERE user_id = 1")
    user_books_count = cursor.fetchone()[0]

    print(f"\n=== 検証結果 ===")
    print(f"books テーブル: {books_count} 件")
    print(f"user_books (admin): {user_books_count} 件")

    # 件数が一致することを確認
    if books_count != user_books_count:
        raise ValueError(
            f"データ不整合: books={books_count}, user_books={user_books_count}"
        )

    # books テーブルに note, status, shelf_id カラムが存在しないことを確認
    cursor.execute("PRAGMA table_info(books)")
    columns = [row[1] for row in cursor.fetchall()]

    forbidden_columns = ['note', 'status', 'shelf_id']
    existing_forbidden = [col for col in forbidden_columns if col in columns]

    if existing_forbidden:
        raise ValueError(
            f"books テーブルに削除すべきカラムが残っています: {existing_forbidden}"
        )

    print(f"✓ データ整合性チェック: OK")
    print(f"✓ books テーブルにユーザー固有カラムなし: OK")

    # 外部キー制約のチェック
    cursor.execute("PRAGMA foreign_key_check")
    fk_errors = cursor.fetchall()
    if fk_errors:
        raise ValueError(f"外部キー制約エラー: {fk_errors}")

    print(f"✓ 外部キー制約チェック: OK")


def main():
    """メイン処理"""
    db_path = "backend/sqlite.db"

    print("=" * 60)
    print("マルチユーザー対応データベース移行スクリプト")
    print("=" * 60)
    print()

    # データベースファイルの存在確認
    if not Path(db_path).exists():
        print(f"✗ エラー: データベースファイルが見つかりません: {db_path}")
        return

    # バックアップ作成
    backup_path = backup_database(db_path)
    print()

    # データベース接続
    # 注: 外部キー制約はデフォルトで無効なので、migrate_books_table で明示的に制御
    conn = sqlite3.connect(db_path)

    try:
        # 移行処理実行
        print("=== ステップ1: users テーブル確認 ===")
        verify_users_table(conn)
        print()

        print("=== ステップ2: user_books テーブル作成 ===")
        create_user_books_table(conn)
        print()

        print("=== ステップ3: books から user_books へデータ移行 ===")
        migrate_book_data(conn)
        print()

        print("=== ステップ4: books テーブル更新 ===")
        migrate_books_table(conn)
        print()

        print("=== ステップ5: データ整合性検証 ===")
        verify_migration(conn)
        print()

        # コミット
        conn.commit()

        print("=" * 60)
        print("✓ 移行が正常に完了しました")
        print("=" * 60)
        print(f"\nバックアップ: {backup_path}")
        print("問題が発生した場合は、バックアップから復元できます。")

    except Exception as e:
        # ロールバック
        conn.rollback()
        print()
        print("=" * 60)
        print(f"✗ 移行が失敗しました: {e}")
        print("=" * 60)
        print(f"\nバックアップ: {backup_path}")
        print("データベースは変更されていません。")
        raise

    finally:
        conn.close()


if __name__ == "__main__":
    main()

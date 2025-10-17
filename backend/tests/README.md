# Backend Tests

Book Selector APIのテストスイート

## テスト構成

```
backend/
├── app/              # アプリケーションコード
├── tests/            # テストコード
│   ├── conftest.py   # pytest設定とフィクスチャ
│   ├── test_books.py # 書籍関連のテスト
│   └── test_health.py # ヘルスチェックのテスト
└── pytest.ini        # pytest設定ファイル
```

## テスト実行方法

### 基本的な実行

```bash
cd backend
uv run pytest
```

### より詳細な出力

```bash
# すべてのテストを詳細表示
uv run pytest -v

# 特定のテストファイルのみ実行
uv run pytest tests/test_books.py

# 特定のテスト関数のみ実行
uv run pytest tests/test_books.py::test_create_book

# 失敗したテストのみ再実行
uv run pytest --lf
```

### VSCodeでのテスト実行

1. VSCodeのテストパネルを開く（サイドバーのフラスコアイコン）
2. テスト一覧から実行したいテストを選択
3. 再生ボタンをクリック

## 現在のテストケース

### test_health.py
- `test_health_endpoint`: `/health`エンドポイントの正常性確認

### test_books.py
- `test_get_books_empty`: 空の書籍リストの取得
- `test_get_books_with_data`: データがある場合の書籍リスト取得
- `test_create_book`: 書籍の新規作成
- `test_create_book_invalid_isbn`: 不正なISBNのバリデーション

## テストフィクスチャ

### `test_engine`
インメモリSQLiteエンジンを作成。各テスト関数ごとに新しいデータベースを提供。

### `test_db`
テスト用のデータベースセッション。FastAPIのdependency_overridesを使用して本番DBと切り替え。

### `client`
FastAPIのTestClient。HTTPリクエストをシミュレート。

## 今後追加すべきテストケース

- [ ] `PUT /books/{id}` - 書籍更新のテスト
- [ ] `DELETE /books/{id}` - 書籍削除のテスト
- [ ] `PATCH /books/{id}/picked` - is_pickedステータス更新のテスト
- [ ] `GET /books/random` - ランダム書籍取得のテスト
- [ ] `GET /books/?order_by=title` - ソート機能のテスト
- [ ] `GET /books/?limit=10` - ページネーションのテスト
- [ ] エラーケースのテスト（存在しないID、重複ISBNなど）

# Backend Tests

Book Selector APIのテストスイート

## テスト構成

```
backend/
├── app/              # アプリケーションコード
├── tests/            # テストコード
│   ├── conftest.py    # pytest設定とフィクスチャ
│   ├── test_admin.py  # 管理系エンドポイントのテスト
│   ├── test_books.py  # 書籍関連のテスト
│   ├── test_lookup.py # 検索APIのテスト
│   └── test_shelves.py # 棚関連のテスト
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

### test_books.py
- `test_get_books_empty`: 空の書籍リストの取得
- `test_get_books_with_data`: データがある場合の書籍リスト取得
- `test_create_book`: 書籍の新規作成
- `test_create_book_invalid_isbn`: 不正なISBNのバリデーション

### test_shelves.py
- `test_get_shelves_empty`: 空の棚リスト取得
- `test_get_shelves_with_data`: 棚データがある場合の取得
- `test_create_shelf`: 棚の新規作成
- `test_get_shelf_detail`: 詳細取得
- `test_update_shelf` / `test_update_shelf_not_found`: 更新成功と404
- `test_delete_shelf` / `test_delete_shelf_not_found`: 削除成功と404

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

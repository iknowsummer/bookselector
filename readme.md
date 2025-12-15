# Book Selector

蔵書を管理し、ランダムに書籍を選択できるWebアプリケーションです。

## 概要

Book Selectorは、個人の蔵書コレクションを管理するためのフルスタックWebアプリケーションです。書籍の登録・編集・削除といった基本的な管理機能に加え、登録した書籍からランダムに選択する機能を提供します。

## 主な機能

- 📚 **書籍管理**: 書籍の登録、編集、削除、一覧表示
- 🎲 **ランダム選択**: 登録された書籍からランダムに選択
- 🔍 **書籍検索**: タイトル、著者、ISBN（13桁）による検索
- 📖 **読書ステータス管理**: 未読(unread)、選択済み(picked)、読了(read)の3つの状態で管理
- 🖼️ **画像管理**: 書籍の表紙画像URLを保存
- 📝 **メモ機能**: 各書籍に対象年齢やメモを記録

## 技術スタック

### バックエンド
- **Python 3.x**
- **FastAPI** - REST APIフレームワーク
- **SQLAlchemy** - ORM
- **SQLite** - データベース
- **Pydantic** - データバリデーション
- **uv** - Pythonパッケージマネージャー

### フロントエンド
- **Next.js 15** - Reactフレームワーク（App Router使用）
- **React 19**
- **TypeScript**
- **npm** - パッケージマネージャー

## 必要な環境

- Python 3.10以上
- Node.js 18以上
- uv (Pythonパッケージマネージャー)
- npm

## セットアップ

### 1. リポジトリのクローン

```bash
git clone <repository-url>
cd bookselector
```

### 2. バックエンドのセットアップ

```bash
cd backend

# .envファイルを作成
echo "PICKCOUNT=4" > .env

cd app

# 依存関係をインストール（uvが自動的に処理）
uv run uvicorn main:app --reload
```

### 3. フロントエンドのセットアップ

```bash
cd frontend

# .envファイルを作成
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env

# 依存関係をインストール
npm install
```

### 4. ルートディレクトリの依存関係をインストール

```bash
# プロジェクトルートに戻る
cd ..

# 開発用ツールのインストール
npm install
```

## 起動方法

### 開発環境の起動（推奨）

プロジェクトルートで以下のコマンドを実行すると、バックエンドとフロントエンドが同時に起動し、ブラウザが自動的に開きます：

```bash
npm run dev
```

このコマンドは以下を実行します：
- バックエンドAPIサーバー起動 (http://localhost:8000)
- フロントエンド開発サーバー起動 (http://localhost:3000)
- ブラウザで http://localhost:3000 を自動的に開く
- ブラウザで http://localhost:8000/docs (API仕様書) を自動的に開く

### 個別起動

#### バックエンドのみ起動

```bash
npm run api-dev
```

または

```bash
cd backend/app
uv run uvicorn main:app --reload
```

#### フロントエンドのみ起動

```bash
npm run next-dev
```

または

```bash
cd frontend
npm run dev
```

## API仕様

バックエンドサーバー起動後、以下のURLでAPIドキュメントを確認できます：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### 主要エンドポイント

- `GET /health` - ヘルスチェック
- `GET /books/random` - ランダムに書籍を取得（デフォルトは未読のみ）
- `GET /books/` - 書籍一覧を取得
- `GET /books/{id}` - 書籍を個別取得
- `POST /books/` - 新しい書籍を登録
- `PUT /books/{id}` - 書籍情報を更新
- `DELETE /books/{id}` - 書籍を削除
- `PATCH /books/{id}/status` - 読書ステータスを更新（unread/picked/read）

## プロジェクト構造

```
bookselector/
├── backend/              # バックエンド（FastAPI）
│   ├── .env             # 環境変数
│   └── app/
│       ├── main.py      # アプリケーションエントリーポイント
│       ├── database.py  # データベース設定
│       ├── models.py    # データベースモデル
│       ├── schemas.py   # Pydanticスキーマ
│       ├── router/      # APIルーター
│       ├── exceptions/  # エラーハンドリング
│       ├── pyproject.toml  # Python依存関係
│       └── sqlite.db    # SQLiteデータベース
├── frontend/            # フロントエンド（Next.js）
│   ├── .env            # 環境変数
│   ├── app/            # Next.js App Router
│   │   ├── page.tsx    # ホームページ
│   │   ├── layout.tsx  # レイアウト
│   │   └── books/      # 書籍関連ページ
│   ├── components/     # Reactコンポーネント
│   ├── lib/            # ユーティリティ
│   │   └── api/        # APIクライアント
│   └── types/          # TypeScript型定義
├── scripts/            # ユーティリティスクリプト
│   ├── get_isbn.py     # Google Books APIから書籍情報取得
│   ├── import_csv_to_sqlite.py  # CSVインポート
│   └── delete_table.py # テーブル削除
├── package.json        # ルートパッケージ設定
└── README.md           # このファイル
```

## 環境変数

### バックエンド（`backend/.env`）

```env
PICKCOUNT=4  # ランダム選択時に返す書籍の数
```

### フロントエンド（`frontend/.env`）

```env
NEXT_PUBLIC_API_URL=http://localhost:8000  # バックエンドAPIのURL
```

## データベース

- SQLiteを使用
- データベースファイル: `data/sqlite.db`
- 初回起動時に自動的にテーブルが作成されます

### データモデル

#### Book（書籍）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| id | Integer | 主キー |
| title | String(200) | タイトル（必須） |
| author | String(200) | 著者（任意） |
| description | Text | 説明（任意） |
| target_age | String(50) | 対象年齢（任意） |
| isbn | String(13) | ISBN-13（任意、ユニーク） |
| image_url | String(500) | 画像URL（任意） |
| note | Text | メモ（任意） |
| status | String(20) | 読書ステータス（unread/picked/read、デフォルト: unread） |
| created_at | DateTime | 作成日時（自動生成） |

## 開発

### バックエンドの開発

```bash
cd backend/app

# サーバーを起動（自動リロード有効）
uv run uvicorn main:app --reload

# 新しい依存関係を追加
uv add <package-name>
```

### フロントエンドの開発

```bash
cd frontend

# 開発サーバーを起動
npm run dev

# 本番ビルド
npm run build

# 本番サーバーを起動
npm start

# リンター実行
npm run lint

# 依存関係を追加
npm install <package-name>
```

### ユーティリティスクリプト

```bash
# Google Books APIから書籍情報を取得してCSVを更新
python scripts/get_isbn.py

# CSVからデータベースにインポート
python scripts/import_csv_to_sqlite.py

# データベーステーブルを削除
python scripts/delete_table.py
```

## トラブルシューティング

### ポートが既に使用されている

- バックエンド: 8000番ポートが使用されていないか確認
- フロントエンド: 3000番ポートが使用されていないか確認

```bash
# ポート使用状況を確認（Windows）
netstat -ano | findstr :8000
netstat -ano | findstr :3000

# ポート使用状況を確認（Mac/Linux）
lsof -i :8000
lsof -i :3000
```

### データベースのリセット

```bash
# データベースファイルを削除（バックアップから復元する場合）
cd backend/app
rm sqlite.db
cp sqlite-bk.db sqlite.db

# または、アプリを再起動すると新しいデータベースが作成されます
```

### CORS エラー

フロントエンドからバックエンドへのリクエストでCORSエラーが発生する場合：

1. バックエンドの`main.py`でCORS設定を確認
2. フロントエンドが`http://localhost:3000`で動作していることを確認
3. 環境変数`NEXT_PUBLIC_API_URL`が正しく設定されているか確認

## ライセンス

ISC

## 作者

作成者情報は`package.json`を参照してください。

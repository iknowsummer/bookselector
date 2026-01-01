# user_books 分離と登録フロー整理の方針まとめ

## 背景
- 書誌情報（タイトル・著者・概要など）は ISBN 由来の確定情報のみを登録し、ユーザーによる手動上書きを禁止する。
- ユーザー固有の情報（メモ・棚・ステータス）は user_books に集約し、書誌情報と分離して整合性を保つ。
- 登録フローは「ISBN 入力 → 書誌情報登録 → user_books 登録」を同画面で連続的に行う。

## 方針
- books: ISBN から取得した書誌情報のみを保存する。
- user_books: note / shelf_id / status のみを扱う。
- 書誌情報は更新不可（books の更新 API はエラーを返す）。
- UI では書誌情報を表示のみ（編集不可）とし、メモ・棚・ステータスのみ編集可能にする。

## バックエンド構成
- `POST /books/`: ISBN で Google Books API を参照し、books に書誌情報を登録。
- `PUT /books/{id}`: 書誌情報更新は禁止（400）。
- `POST /user-books/`: user_books を作成。
- `PUT /user-books/{book_id}`: user_books を更新。
- `DELETE /user-books/{book_id}`: user_books を削除。

## フロントエンド構成
- ISBN 入力後に books を登録し、続けて user_books を登録する同画面連続フロー。
- 書誌情報は表示専用、ユーザー入力はメモ・棚・ステータスのみ。

## 補足
- 二段階フローを維持しつつ、最終的な書誌情報は必ず ISBN 由来で保証する設計。

"""
/books/ エンドポイントのテスト
"""


# ============================================================
# GET /books/ - 書籍一覧取得
# ============================================================


def test_get_books_empty(client, test_db):
    """
    データが空の場合、空のリストが返ることを確認

    test_dbを引数に追加することで、DBが初期化される
    （clientだけではDBセットアップのタイミングが保証されない）
    """
    response = client.get("/books/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_books_with_data(client, sample_books):
    """
    データがある場合、書籍リストが返ることを確認

    sample_booksフィクスチャを使用して、標準的な2冊のデータでテスト
    フィクスチャの値を直接参照することでDRYを保つ
    """
    book1, book2 = sample_books

    response = client.get("/books/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    # デフォルトはcreated_at descなので、book2が先に来る
    assert data[0]["title"] == book2.title
    assert data[0]["author"] == book2.author
    assert data[0]["isbn"] == book2.isbn
    assert data[0]["status"] == "unread"  # デフォルト

    assert data[1]["title"] == book1.title
    assert data[1]["author"] == book1.author
    assert data[1]["isbn"] == book1.isbn
    assert data[1]["status"] == "unread"  # デフォルト


# ============================================================
# GET /books/{id} - 書籍個別取得
# ============================================================


def test_get_book_by_id(client, sample_books):
    """
    IDを指定して書籍を取得できることを確認
    """
    book1, _ = sample_books

    response = client.get(f"/books/{book1.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == book1.id
    assert data["title"] == book1.title
    assert data["author"] == book1.author
    assert data["isbn"] == book1.isbn
    assert data["status"] == "unread"  # デフォルト


def test_get_book_by_id_not_found(client):
    """
    存在しないIDで書籍を取得しようとした場合、404エラーになることを確認
    """
    response = client.get("/books/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


def test_get_books_with_limit(client, sample_books):
    """
    limit パラメータで取得件数を制限できることを確認
    """
    _ = sample_books  # DB初期化のため

    response = client.get("/books/?limit=1")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1


def test_get_books_with_order(client, sample_books):
    """
    order パラメータでソート順を変更できることを確認
    """
    book1, book2 = sample_books

    # 昇順（asc）の場合、book1が先に来る
    response = client.get("/books/?order=asc")
    assert response.status_code == 200

    data = response.json()
    assert data[0]["id"] == book1.id
    assert data[1]["id"] == book2.id


# ============================================================
# POST /books/ - 書籍新規作成
# ============================================================


def test_create_book(client):
    """
    書籍を新規作成できることを確認
    """
    book_data = {
        "title": "新しい本",
        "author": "テスト著者",
        "description": "テスト説明",
        "isbn": "9781111111111"
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == book_data["title"]
    assert data["author"] == book_data["author"]
    assert data["isbn"] == book_data["isbn"]
    assert "id" in data
    assert "created_at" in data


def test_create_book_invalid_isbn(client):
    """
    不正なISBN（13桁以外）でエラーになることを確認
    """
    book_data = {
        "title": "新しい本",
        "isbn": "123"  # 13桁でない
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 422  # Validation error


# ============================================================
# PUT /books/{id} - 書籍更新
# ============================================================


def test_update_book(client, sample_books):
    """
    書籍を更新できることを確認
    """
    book1, _ = sample_books

    update_data = {
        "title": "更新されたタイトル",
        "author": "更新された著者",
        "description": "更新された説明",
        "isbn": "9789999999999"
    }

    response = client.put(f"/books/{book1.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == book1.id
    assert data["title"] == update_data["title"]
    assert data["author"] == update_data["author"]
    assert data["isbn"] == update_data["isbn"]


def test_update_book_not_found(client):
    """
    存在しない書籍を更新しようとした場合、404エラーになることを確認
    """
    update_data = {
        "title": "更新されたタイトル",
    }

    response = client.put("/books/99999", json=update_data)
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


# ============================================================
# DELETE /books/{id} - 書籍削除
# ============================================================


def test_delete_book(client, sample_books):
    """
    書籍を削除できることを確認
    """
    book1, _ = sample_books

    response = client.delete(f"/books/{book1.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Book deleted successfully"

    # 削除後、取得できないことを確認
    get_response = client.get("/books/")
    data = get_response.json()
    assert len(data) == 1  # book2のみ残る


def test_delete_book_not_found(client):
    """
    存在しない書籍を削除しようとした場合、404エラーになることを確認
    """
    response = client.delete("/books/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


# ============================================================
# PATCH /books/{id}/status - ステータス更新
# ============================================================


def test_update_book_status_to_picked(client, sample_books):
    """
    書籍のステータスをpickedに更新できることを確認
    """
    book1, _ = sample_books

    response = client.patch(f"/books/{book1.id}/status", json={"status": "picked"})
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == book1.id
    assert data["status"] == "picked"


def test_update_book_status_to_read(client, sample_books):
    """
    書籍のステータスをreadに更新できることを確認
    """
    book1, _ = sample_books

    response = client.patch(f"/books/{book1.id}/status", json={"status": "read"})
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == book1.id
    assert data["status"] == "read"


def test_update_book_status_to_unread(client, sample_books):
    """
    書籍のステータスをunreadに戻せることを確認
    """
    book1, _ = sample_books

    # まずpickedに変更
    client.patch(f"/books/{book1.id}/status", json={"status": "picked"})

    # unreadに戻す
    response = client.patch(f"/books/{book1.id}/status", json={"status": "unread"})
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "unread"


def test_update_book_status_not_found(client):
    """
    存在しない書籍のステータスを更新しようとした場合、404エラーになることを確認
    """
    response = client.patch("/books/99999/status", json={"status": "picked"})
    assert response.status_code == 404
    assert response.json()["detail"] == "Book not found"


# ============================================================
# GET /books/random - ランダム取得
# ============================================================


def test_random_books(client, book_factory):
    """
    ランダムに書籍を取得できることを確認
    """
    # 5冊作成（デフォルトのPICKCOUNT=4より多く）
    for i in range(5):
        book_factory(
            title=f"ランダム本{i}",
            isbn=f"978{i:010d}"
        )

    response = client.get("/books/random")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) <= 4  # PICKCOUNT以下


def test_random_books_exclude_non_unread(client, book_factory):
    """
    unread以外の書籍を除外してランダム取得できることを確認
    """
    # picked状態の書籍を作成
    book_factory(title="Picked本", status="picked", isbn="9781111111111")

    # read状態の書籍を作成
    book_factory(title="Read本", status="read", isbn="9782222222222")

    # unread状態の書籍を作成
    unread_book = book_factory(title="Unread本", status="unread", isbn="9783333333333")

    # include_all_status=0（デフォルト）の場合、unreadのみ取得
    response = client.get("/books/random?include_all_status=0")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == unread_book.id
    assert data[0]["status"] == "unread"


def test_random_books_include_all_status(client, book_factory):
    """
    include_all_status=1の場合、すべてのステータスを取得できることを確認
    """
    # 各ステータスの書籍を作成
    book_factory(title="Unread本", status="unread", isbn="9781111111111")
    book_factory(title="Picked本", status="picked", isbn="9782222222222")
    book_factory(title="Read本", status="read", isbn="9783333333333")

    # include_all_status=1の場合、すべて取得
    response = client.get("/books/random?include_all_status=1")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 3

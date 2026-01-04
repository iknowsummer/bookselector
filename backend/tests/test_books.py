"""
/books/ エンドポイントのテスト
"""

from app.lookup.schemas import GoogleBooksResponse
from app.router import books as books_router

# ============================================================
# GET /books/ - 書籍一覧取得
# ============================================================


def test_get_books_empty(client, admin_user, test_db):
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

    # デフォルトはcreated_at descだが、同じ時刻の場合は id で決まる
    # 両方の書籍が返ってくることを確認
    titles = {book["title"] for book in data}
    assert book1.title in titles
    assert book2.title in titles

    # ステータスがデフォルトであることを確認
    for book in data:
        assert book["status"] == "unread"


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


def test_get_book_by_id_not_found(client, admin_user):
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


def test_create_book(client, admin_user, monkeypatch):
    """
    書籍を新規作成できることを確認
    """

    def mock_fetch_book_by_isbn(isbn: str) -> GoogleBooksResponse:
        return GoogleBooksResponse(
            title="取得本",
            author="取得著者",
            description="取得説明",
            isbn=isbn,
            image_url=None,
        )

    monkeypatch.setattr(books_router, "fetch_book_by_isbn", mock_fetch_book_by_isbn)

    book_data = {
        "isbn": "9781111111111",
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "取得本"
    assert data["author"] == "取得著者"
    assert data["isbn"] == book_data["isbn"]
    assert data["note"] is None
    assert data["status"] == "unread"
    assert "id" in data
    assert "created_at" in data


def test_create_book_invalid_isbn(client, admin_user):
    """
    不正なISBN（13桁以外）でエラーになることを確認
    """
    book_data = {
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
        "note": "更新されたメモ",
    }

    response = client.put(f"/books/{book1.id}", json=update_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "書籍情報は更新できません"


def test_update_book_not_found(client, admin_user):
    """
    書籍更新が許可されていないことを確認
    """
    update_data = {
        "note": "更新されたメモ",
    }

    response = client.put("/books/99999", json=update_data)
    assert response.status_code == 400
    assert response.json()["detail"] == "書籍情報は更新できません"


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


def test_delete_book_not_found(client, admin_user):
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


def test_update_book_status_not_found(client, admin_user):
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


# ============================================================
# Shelf関連のテスト
# ============================================================


def test_create_book_with_shelf_id(client, admin_user, shelf_factory, monkeypatch):
    """
    shelf_idを指定せずに書誌情報のみ登録できることを確認
    """
    _ = shelf_factory(name="test_shelf", user_id=admin_user.id)

    def mock_fetch_book_by_isbn(isbn: str) -> GoogleBooksResponse:
        return GoogleBooksResponse(
            title="棚付き取得本",
            author="取得著者",
            description="取得説明",
            isbn=isbn,
            image_url=None,
        )

    monkeypatch.setattr(books_router, "fetch_book_by_isbn", mock_fetch_book_by_isbn)

    book_data = {
        "isbn": "9781111111111",
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "棚付き取得本"
    assert data["shelf_id"] is None


def test_create_book_without_shelf_id(client, admin_user, monkeypatch):
    """
    書誌情報のみ登録できることを確認
    """
    def mock_fetch_book_by_isbn(isbn: str) -> GoogleBooksResponse:
        return GoogleBooksResponse(
            title="棚なし取得本",
            author="取得著者",
            description="取得説明",
            isbn=isbn,
            image_url=None,
        )

    monkeypatch.setattr(books_router, "fetch_book_by_isbn", mock_fetch_book_by_isbn)

    book_data = {
        "isbn": "9781111111112",
    }
    response = client.post("/books/", json=book_data)
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "棚なし取得本"
    assert data["shelf_id"] is None


def test_update_book_shelf_id(client, admin_user, book_factory, shelf_factory):
    """
    書籍のshelf_idを更新できることを確認
    """
    book = book_factory(title="テスト本")
    shelf = shelf_factory(name="new_shelf", user_id=admin_user.id)

    update_data = {
        "shelf_id": shelf.id
    }

    response = client.put(f"/books/{book.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["shelf_id"] == shelf.id


def test_filter_books_by_shelf_id(client, admin_user, book_factory, shelf_factory):
    """
    shelf_idでフィルタリングして書籍を取得できることを確認
    """
    shelf1 = shelf_factory(name="shelf1", user_id=admin_user.id)
    shelf2 = shelf_factory(name="shelf2", user_id=admin_user.id)

    book1 = book_factory(title="本1", shelf_id=shelf1.id, isbn="9781111111111")
    book2 = book_factory(title="本2", shelf_id=shelf1.id, isbn="9782222222222")
    book3 = book_factory(title="本3", shelf_id=shelf2.id, isbn="9783333333333")
    book4 = book_factory(title="本4", shelf_id=None, isbn="9784444444444")

    # shelf1の本のみ取得
    response = client.get(f"/books/?shelf_id={shelf1.id}")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 2
    book_ids = [b["id"] for b in data]
    assert book1.id in book_ids
    assert book2.id in book_ids
    assert book3.id not in book_ids
    assert book4.id not in book_ids


def test_shelf_deletion_sets_book_shelf_id_to_null(client, admin_user, book_factory, shelf_factory, test_db):
    """
    棚を削除したときに書籍のshelf_idがNULLになることを確認
    """
    from app.models import UserBook

    shelf = shelf_factory(name="delete_test_shelf", user_id=admin_user.id)
    book = book_factory(title="テスト本", shelf_id=shelf.id)
    book_id = book.id

    # 書籍のshelf_idが設定されていることを確認
    response = client.get(f"/books/{book_id}")
    assert response.json()["shelf_id"] == shelf.id

    # 棚を削除
    delete_response = client.delete(f"/shelves/{shelf.id}")
    assert delete_response.status_code == 200

    # DBセッションをリフレッシュしてキャッシュをクリア
    test_db.expire_all()

    # UserBook の shelf_id が NULL になっていることを確認
    user_book = (
        test_db.query(UserBook)
        .filter(UserBook.book_id == book_id, UserBook.user_id == admin_user.id)
        .first()
    )
    assert user_book is not None
    assert user_book.shelf_id is None

"""
/lookup/ エンドポイントのテスト
"""


# ============================================================
# GET /lookup/isbn/{isbn} - ISBN検索
# ============================================================


def test_lookup_book_by_isbn_success(client, monkeypatch):
    """
    正常系: ISBNから書籍情報を取得できることを確認
    """
    from app.lookup.schemas import GoogleBooksResponse
    from app.lookup import router

    # Google Books APIのfetch_book_by_isbn関数をモック
    def mock_fetch_book_by_isbn(isbn: str):
        return GoogleBooksResponse(
            title="テスト書籍",
            author="テスト著者1, テスト著者2",
            description="テスト説明",
            isbn=isbn,
            image_url="https://example.com/image.jpg",
        )

    monkeypatch.setattr(router, "fetch_book_by_isbn", mock_fetch_book_by_isbn)

    # ISBNで検索
    isbn = "9784123456789"
    response = client.get(f"/lookup/isbn/{isbn}")
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "テスト書籍"
    assert data["author"] == "テスト著者1, テスト著者2"
    assert data["description"] == "テスト説明"
    assert data["isbn"] == isbn
    assert data["image_url"] == "https://example.com/image.jpg"


def test_lookup_book_by_isbn_not_found(client, monkeypatch):
    """
    書籍が見つからない場合、404エラーになることを確認
    """
    from fastapi import HTTPException
    from app.lookup import router

    # Google Books APIが404を返すケース
    def mock_fetch_book_by_isbn(isbn: str):
        raise HTTPException(
            status_code=404,
            detail=f"Book not found for ISBN: {isbn}"
        )

    monkeypatch.setattr(router, "fetch_book_by_isbn", mock_fetch_book_by_isbn)

    isbn = "9784999999999"
    response = client.get(f"/lookup/isbn/{isbn}")
    assert response.status_code == 404
    assert "Book not found for ISBN" in response.json()["detail"]


def test_lookup_book_by_isbn_invalid_format(client):
    """
    ISBNフォーマットが不正な場合、400エラーになることを確認
    """
    # 13桁でないISBN
    response = client.get("/lookup/isbn/123")
    assert response.status_code == 400
    assert "ISBNは13桁の数字である必要があります" in response.json()["detail"]

    # 数字以外を含む
    response = client.get("/lookup/isbn/978412345678X")
    assert response.status_code == 400
    assert "ISBNは13桁の数字である必要があります" in response.json()["detail"]


def test_lookup_book_by_isbn_api_error(client, monkeypatch):
    """
    Google Books API接続エラーの場合、500エラーになることを確認
    """
    from fastapi import HTTPException
    from app.lookup import router

    # Google Books APIがAPI接続エラーで500を返すケース
    def mock_fetch_book_by_isbn(isbn: str):
        raise HTTPException(
            status_code=500,
            detail="Google Books APIへの接続に失敗しました"
        )

    monkeypatch.setattr(router, "fetch_book_by_isbn", mock_fetch_book_by_isbn)

    isbn = "9784123456789"
    response = client.get(f"/lookup/isbn/{isbn}")
    assert response.status_code == 500
    assert "Google Books APIへの接続に失敗しました" in response.json()["detail"]


def test_lookup_book_by_isbn_with_minimal_info(client, monkeypatch):
    """
    最小限の書籍情報でも正常に処理できることを確認
    """
    from app.lookup.schemas import GoogleBooksResponse
    from app.lookup import router

    # 著者や説明、画像URLがないケース
    def mock_fetch_book_by_isbn(isbn: str):
        return GoogleBooksResponse(
            title="タイトルのみの本",
            author=None,
            description=None,
            isbn=isbn,
            image_url=None,
        )

    monkeypatch.setattr(router, "fetch_book_by_isbn", mock_fetch_book_by_isbn)

    isbn = "9784123456789"
    response = client.get(f"/lookup/isbn/{isbn}")
    assert response.status_code == 200

    data = response.json()
    assert data["title"] == "タイトルのみの本"
    assert data["author"] is None
    assert data["description"] is None
    assert data["isbn"] == isbn
    assert data["image_url"] is None


def test_lookup_book_by_isbn_image_priority(client, monkeypatch):
    """
    画像URLの優先順位が正しく処理されることを確認（大きい画像優先）
    """
    from app.lookup.schemas import GoogleBooksResponse
    from app.lookup import router

    # largeサイズの画像が優先されるケース
    def mock_fetch_book_by_isbn(isbn: str):
        return GoogleBooksResponse(
            title="画像付き書籍",
            author=None,
            description=None,
            isbn=isbn,
            image_url="https://example.com/large.jpg",
        )

    monkeypatch.setattr(router, "fetch_book_by_isbn", mock_fetch_book_by_isbn)

    isbn = "9784123456789"
    response = client.get(f"/lookup/isbn/{isbn}")
    assert response.status_code == 200

    data = response.json()
    # largeが優先される
    assert data["image_url"] == "https://example.com/large.jpg"

"""
/books/ エンドポイントのテスト
"""


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
    """
    response = client.get("/books/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    # デフォルトはcreated_at descなので、book2が先に来る
    assert data[0]["title"] == "テスト本2"
    assert data[0]["author"] == "著者2"
    assert data[0]["isbn"] == "9780987654321"

    assert data[1]["title"] == "テスト本1"
    assert data[1]["author"] == "著者1"
    assert data[1]["isbn"] == "9781234567890"


def test_create_book(client):
    """
    書籍を新規作成できることを確認
    """
    book_data = {
        "title": "新しい本",
        "author": "テスト著者",
        "description": "テスト説明",
        "isbn": "9781234567890"
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

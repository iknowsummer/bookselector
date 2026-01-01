"""
/user-books/ エンドポイントのテスト
"""

from app.models import Book, UserBook


def test_create_user_book(client, admin_user, test_db):
    """
    user_booksを作成できることを確認
    """
    book = Book(
        title="テスト本",
        author="テスト著者",
        description="テスト説明",
        isbn="9781111111111",
        image_url=None,
    )
    test_db.add(book)
    test_db.commit()
    test_db.refresh(book)

    payload = {
        "book_id": book.id,
        "note": "メモ",
    }
    response = client.post("/user-books/", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["book_id"] == book.id
    assert data["note"] == "メモ"
    assert data["status"] == "unread"


def test_update_user_book(client, admin_user, test_db):
    """
    user_booksを更新できることを確認
    """
    book = Book(
        title="テスト本",
        author="テスト著者",
        description="テスト説明",
        isbn="9782222222222",
        image_url=None,
    )
    test_db.add(book)
    test_db.commit()
    test_db.refresh(book)

    user_book = UserBook(
        user_id=admin_user.id,
        book_id=book.id,
        note="初期メモ",
        status="unread",
    )
    test_db.add(user_book)
    test_db.commit()

    payload = {
        "note": "更新メモ",
        "status": "picked",
    }
    response = client.put(f"/user-books/{book.id}", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["book_id"] == book.id
    assert data["note"] == "更新メモ"
    assert data["status"] == "picked"


def test_delete_user_book(client, admin_user, test_db):
    """
    user_booksを削除できることを確認
    """
    book = Book(
        title="テスト本",
        author="テスト著者",
        description="テスト説明",
        isbn="9783333333333",
        image_url=None,
    )
    test_db.add(book)
    test_db.commit()
    test_db.refresh(book)

    user_book = UserBook(
        user_id=admin_user.id,
        book_id=book.id,
        note="削除メモ",
        status="unread",
    )
    test_db.add(user_book)
    test_db.commit()

    response = client.delete(f"/user-books/{book.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "UserBook deleted successfully"

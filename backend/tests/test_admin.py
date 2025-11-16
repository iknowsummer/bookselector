"""
管理系エンドポイントのテスト
"""
from datetime import datetime


def test_health_endpoint(client):
    """
    /health エンドポイントが正常に応答することを確認
    """
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert data["message"] == "OK! The server is running."


def test_db_status_endpoint(client):
    """
    /db-status エンドポイントが正常に応答することを確認
    レコードがない場合、last_modifiedはNoneになる
    """
    response = client.get("/db-status")
    assert response.status_code == 200
    data = response.json()

    # last_modified フィールドが存在することを確認
    assert "last_modified" in data

    # レコードがない場合はNoneになる
    last_modified = data["last_modified"]
    if last_modified is not None:
        # 値がある場合はISO 8601形式の日時文字列であることを確認
        assert isinstance(last_modified, str)
        # パース可能な日時であることを確認
        try:
            datetime.fromisoformat(last_modified)
        except ValueError:
            assert False, f"Invalid datetime format: {last_modified}"

    # record_count フィールドが存在することを確認
    assert "record_count" in data
    assert isinstance(data["record_count"], int)
    assert data["record_count"] >= 0


def test_db_status_with_books(client, sample_books):
    """
    /db-status エンドポイントがレコード数を正しく返すことを確認
    """
    response = client.get("/db-status")
    assert response.status_code == 200
    data = response.json()

    # sample_booksは2冊の本を含む
    assert data["record_count"] == 2

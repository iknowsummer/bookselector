"""
/users/ エンドポイントのテスト
"""

from fastapi.testclient import TestClient


def test_create_user(client: TestClient):
    """ユーザー作成のテスト"""
    response = client.post("/users/", json={"name": "test_user"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_user"
    assert "id" in data
    assert "created_at" in data


def test_read_users(client: TestClient, user_factory):
    """ユーザー一覧取得のテスト"""
    user_factory(name="user1")
    user_factory(name="user2")

    response = client.get("/users/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_read_user(client: TestClient, user_factory):
    """ユーザー詳細取得のテスト"""
    user = user_factory(name="test_user")

    response = client.get(f"/users/{user.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test_user"
    assert data["id"] == user.id


def test_update_user(client: TestClient, user_factory):
    """ユーザー更新のテスト"""
    user = user_factory(name="old_name")

    response = client.put(f"/users/{user.id}", json={"name": "new_name"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "new_name"


def test_delete_user(client: TestClient, user_factory):
    """ユーザー削除のテスト"""
    user = user_factory(name="to_delete")

    response = client.delete(f"/users/{user.id}")
    assert response.status_code == 200

    # 削除を確認
    response = client.get(f"/users/{user.id}")
    assert response.status_code == 404


def test_user_not_found(client: TestClient):
    """存在しないユーザーのテスト"""
    response = client.get("/users/999")
    assert response.status_code == 404


def test_delete_user_not_found(client: TestClient):
    """存在しないユーザーの削除テスト"""
    response = client.delete("/users/999")
    assert response.status_code == 404


def test_update_user_not_found(client: TestClient):
    """存在しないユーザーの更新テスト"""
    response = client.put("/users/999", json={"name": "new_name"})
    assert response.status_code == 404

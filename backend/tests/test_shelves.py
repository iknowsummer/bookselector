import pytest
from fastapi.testclient import TestClient


def test_get_shelves_empty(client: TestClient, admin_user):
    """admin_user ensures context exists"""
    response = client.get("/shelves/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_shelves_with_data(client: TestClient, sample_shelves, admin_user):
    response = client.get("/shelves/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == sample_shelves[0].name
    assert data[0]["user_id"] == admin_user.id
    assert "created_at" in data[0]


def test_create_shelf(client: TestClient, admin_user):
    payload = {"name": "study", "memo": "書斎の棚"}
    response = client.post("/shelves/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == payload["name"]
    assert data["memo"] == payload["memo"]
    assert data["user_id"] == admin_user.id
    assert "created_at" in data


def test_get_shelf_detail(client: TestClient, shelf_factory, admin_user):
    shelf = shelf_factory(user_id=admin_user.id, name="kidroom", memo="子ども部屋")
    response = client.get(f"/shelves/{shelf.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "kidroom"
    assert data["user_id"] == admin_user.id
    assert "created_at" in data


def test_update_shelf(client: TestClient, shelf_factory, admin_user):
    shelf = shelf_factory(user_id=admin_user.id, name="garage", memo="ガレージ")
    response = client.put(
        f"/shelves/{shelf.id}", json={"name": "garage-new", "memo": "整理済み"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "garage-new"
    assert data["memo"] == "整理済み"
    assert data["user_id"] == admin_user.id


def test_update_shelf_not_found(client: TestClient, admin_user):
    response = client.put("/shelves/999", json={"name": "missing"})
    assert response.status_code == 404


def test_delete_shelf(client: TestClient, shelf_factory, admin_user):
    shelf = shelf_factory(user_id=admin_user.id, name="closet", memo="クローゼット")
    response = client.delete(f"/shelves/{shelf.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Shelf deleted successfully"


def test_delete_shelf_not_found(client: TestClient, admin_user):
    response = client.delete("/shelves/999")
    assert response.status_code == 404


# New tests for user isolation


def test_shelf_names_unique_per_user(
    client: TestClient, user_factory, shelf_factory, admin_user
):
    """Shelf names are unique per user, not globally"""
    user2 = user_factory(name="user2")

    shelf1 = shelf_factory(user_id=admin_user.id, name="living", memo="Admin's living")
    shelf2 = shelf_factory(user_id=user2.id, name="living", memo="User2's living")

    assert shelf1.name == shelf2.name
    assert shelf1.user_id != shelf2.user_id


def test_shelf_names_must_be_unique_within_user(
    client: TestClient, shelf_factory, admin_user, test_db
):
    """Same user cannot create duplicate shelf names"""
    from sqlalchemy.exc import IntegrityError

    shelf_factory(user_id=admin_user.id, name="living", memo="First")

    with pytest.raises(IntegrityError):
        shelf_factory(user_id=admin_user.id, name="living", memo="Second")


def test_get_shelves_only_returns_user_shelves(
    client: TestClient, user_factory, shelf_factory, admin_user
):
    """GET /shelves/ only returns current user's shelves"""
    user2 = user_factory(name="user2")
    shelf_factory(
        user_id=user2.id, name="user2_shelf"
    )  # Create but don't need reference
    admin_shelf = shelf_factory(user_id=admin_user.id, name="admin_shelf")

    response = client.get("/shelves/")
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1  # Only admin's shelf
    assert data[0]["id"] == admin_shelf.id


def test_user_cannot_access_other_user_shelf(
    client: TestClient, user_factory, shelf_factory, admin_user
):
    """User cannot GET/PUT/DELETE another user's shelf"""
    user2 = user_factory(name="user2")
    user2_shelf = shelf_factory(user_id=user2.id, name="user2_private")

    # Admin tries to access user2's shelf (should fail)
    assert client.get(f"/shelves/{user2_shelf.id}").status_code == 404
    assert (
        client.put(f"/shelves/{user2_shelf.id}", json={"name": "hacked"}).status_code
        == 404
    )
    assert client.delete(f"/shelves/{user2_shelf.id}").status_code == 404


def test_user_deletion_cascades_to_shelves(
    client: TestClient, user_factory, shelf_factory, test_db
):
    """Deleting user deletes their shelves (CASCADE)"""
    from app.models import Shelf

    user = user_factory(name="temporary")
    shelf = shelf_factory(user_id=user.id, name="temp_shelf")
    shelf_id = shelf.id

    test_db.delete(user)
    test_db.commit()

    # Shelf should be deleted
    assert test_db.query(Shelf).filter(Shelf.id == shelf_id).first() is None

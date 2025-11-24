from fastapi.testclient import TestClient


def test_get_shelves_empty(client: TestClient):
    response = client.get("/shelves/")
    assert response.status_code == 200
    assert response.json() == []


def test_get_shelves_with_data(client: TestClient, sample_shelves):
    response = client.get("/shelves/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == sample_shelves[0].name


def test_create_shelf(client: TestClient):
    payload = {"name": "study", "memo": "書斎の棚"}
    response = client.post("/shelves/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["id"] > 0
    assert data["name"] == payload["name"]
    assert data["memo"] == payload["memo"]


def test_get_shelf_detail(client: TestClient, shelf_factory):
    shelf = shelf_factory(name="kidroom", memo="子ども部屋")
    response = client.get(f"/shelves/{shelf.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "kidroom"


def test_update_shelf(client: TestClient, shelf_factory):
    shelf = shelf_factory(name="garage", memo="ガレージ")
    response = client.put(
        f"/shelves/{shelf.id}", json={"name": "garage-new", "memo": "整理済み"}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "garage-new"
    assert data["memo"] == "整理済み"


def test_update_shelf_not_found(client: TestClient):
    response = client.put("/shelves/999", json={"name": "missing"})
    assert response.status_code == 404


def test_delete_shelf(client: TestClient, shelf_factory):
    shelf = shelf_factory(name="closet", memo="クローゼット")
    response = client.delete(f"/shelves/{shelf.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Shelf deleted successfully"


def test_delete_shelf_not_found(client: TestClient):
    response = client.delete("/shelves/999")
    assert response.status_code == 404

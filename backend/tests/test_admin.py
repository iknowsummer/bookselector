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
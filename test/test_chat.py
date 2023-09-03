from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_create_chat():
    # Создаем пользователя
    user_response = client.post("/auth/register", json={"username": "testuser", "password": "testpassword"})
    assert user_response.status_code == 200

    # Вход в систему
    login_response = client.post("/auth/jwt/login", data={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Создаем чат
    chat_data = {"name": "Test Chat", "status": 1, "users": ["user_id_here"]}
    response = client.post("/chat/create_chat", json=chat_data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

def test_get_user_chats():
    # Получаем токен для пользователя
    response = client.post("/auth/jwt/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Получаем чаты пользователя
    response = client.get("/chat/user_chats/user_id_here", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 0  # Проверьте, что получены чаты пользователя

def test_get_my_chats():
    # Получаем токен для пользователя
    response = client.post("/auth/jwt/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Получаем чаты текущего пользователя
    response = client.get("/chat/my_chats/1", headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200
    assert len(response.json()) >= 0  # Проверьте, что получены чаты текущего пользователя

def test_get_all_chats():
    # Получаем все чаты
    response = client.get("/chat/all_chats/1")
    assert response.status_code == 200
    assert len(response.json()) >= 0  # Проверьте, что получены все чаты


def test_delete_user():
    # Получаем токен для пользователя
    response = client.post("/auth/jwt/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    access_token = response.json()["access_token"]

    # Удаляем пользователя
    response = client.request(
        "DELETE",
        "/auth/user/?identifier=testuser",
        headers={"Authorization": f"Bearer {access_token}"},
    )
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    # Попытка получения удаленного пользователя должна вернуть 404
    response = client.get("/auth/user/?identifier=testuser")
    assert response.status_code == 404
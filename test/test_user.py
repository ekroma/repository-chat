from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_register_user():
    # Отправить POST-запрос для регистрации пользователя
    response = client.post("/auth/register", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

def test_login_user():
    # Отправить POST-запрос для входа пользователя
    response = client.post("/auth/jwt/login", data={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_get_users():
    # Отправить GET-запрос для получения списка пользователей
    response = client.get("/auth/users/")
    assert response.status_code == 200
    assert all("id" in user for user in response.json())

def test_get_user_by_username():
    # Отправить GET-запрос для получения пользователя по имени пользователя
    response = client.get("/auth/user/?username=testuser")
    assert response.status_code == 200
    assert "id" in response.json()

def test_get_user_not_found():
    # Попытка получения несуществующего пользователя
    response = client.get("/auth/user/?username=nonexistentuser")
    assert response.status_code == 404

def test_delete_user():

    # Удаляем пользователя
    response = client.delete("/auth/user/?username=testuser")
    assert response.status_code == 200
    assert response.json()["message"] == "User deleted successfully"

    # Попытка получения удаленного пользователя должна вернуть 404
    response = client.get("/auth/user/?username=testuser")
    assert response.status_code == 404
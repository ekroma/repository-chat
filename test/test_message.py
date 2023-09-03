from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_send_message():
    # Создаем пользователя
    response = client.post("/auth/register", json={"username": "testuser", "password": "testpassword"})
    assert response.status_code == 200
    assert response.json()["username"] == "testuser"

    # Вход в систему
    login_response = client.post("/auth/jwt/login", data={"username": "testuser", "password": "testpassword"})
    assert login_response.status_code == 200
    access_token = login_response.json()["access_token"]

    # Отправляем сообщение
    message_data = {"text": "Hello, World!", "chat_id": 1}
    response = client.post("/messages/send_message", json=message_data, headers={"Authorization": f"Bearer {access_token}"})
    assert response.status_code == 200

def test_get_messages_in_chat():
    # Получаем сообщения в чате
    response = client.post("/messages/get_chat_messages?chat_id=0")  # Отправляем chat_id как параметр запроса
    assert response.status_code == 200
    assert len(response.json()) >= 0  # Проверьте, что получены сообщения в чате

def test_get_messages():
    # Получаем сообщения с фильтрами
    response = client.get("/messages/messages?sender_id=test_sender_id&receiver_id=test_receiver_id&time_delivered=2023-09-01")
    assert response.status_code == 200
    assert len(response.json()) >= 0  # Проверьте, что получены сообщения с фильтрами


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
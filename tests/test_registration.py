import pytest
import sqlite3
import os
from registration.registration import create_db, add_user, authenticate_user, display_users, user_choice

@pytest.fixture(scope="module")
def setup_database():
    """Фикстура для настройки базы данных перед тестами и её очистки после."""
    create_db()
    yield
    try:
        os.remove('users.db')  # Удаляем базу данных после тестов
    except PermissionError:
        pass

@pytest.fixture
def connection():
    """Фикстура для получения соединения с базой данных и его закрытия после теста."""
    conn = sqlite3.connect('users.db')
    yield conn
    conn.close()

def test_create_db(setup_database, connection):
    """Тест создания базы данных и таблицы пользователей."""
    cursor = connection.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='users';")
    table_exists = cursor.fetchone()
    assert table_exists, "Таблица 'users' должна существовать в базе данных."

def test_add_new_user(setup_database, connection):
    """Тест добавления нового пользователя."""
    add_user('testuser', 'testuser@example.com', 'password123')
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users WHERE username='testuser';")
    user = cursor.fetchone()
    assert user, "Пользователь должен быть добавлен в базу данных."

def test_add_existing_user(setup_database):
    """Тест добавления пользователя с существующим логином."""
    add_user('existinguser', 'existinguser@example.com', 'password123')
    result = add_user('existinguser', 'newuser@example.com', 'password456')
    assert result == False, "Добавление пользователя с существующим логином должно завершиться неудачно."

def test_authenticate_user_success(setup_database):
    """Тест успешной аутентификации пользователя."""
    add_user('authuser', 'authuser@example.com', 'securePassword!')
    auth_result = authenticate_user('authuser', 'securePassword!')
    assert auth_result, "Аутентификация пользователя должна быть успешной."

def test_authenticate_user_nonexistent(setup_database):
    """Тест аутентификации несуществующего пользователя."""
    auth_result = authenticate_user('nonexistentuser', 'somePassword')
    assert auth_result == False, "Аутентификация несуществующего пользователя должна завершиться неудачей."

def test_authenticate_user_wrong_password(setup_database):
    """Тест аутентификации пользователя с неправильным паролем."""
    add_user('wrongpassuser', 'wrongpass@example.com', 'correctPassword!')
    auth_result = authenticate_user('wrongpassuser', 'wrongPassword!')
    assert auth_result == False, "Аутентификация с неправильным паролем должна завершиться неудачей."

def test_display_users(setup_database, connection):
    """Тест отображения списка пользователей."""
    add_user('user1', 'user1@example.com', 'password1')
    add_user('user2', 'user2@example.com', 'password2')
    
    users = display_users()  # Теперь функция возвращает список пользователей
    assert len(users) == 3, "Должно отображаться 3 пользователя (включая администратора)."
    assert ('user1', 'user1@example.com') in users, "Пользователь 'user1' должен быть в списке пользователей."
    assert ('user2', 'user2@example.com') in users, "Пользователь 'user2' должен быть в списке пользователей."

def test_add_user_with_empty_fields(setup_database):
    """Тест добавления пользователя с пустыми полями."""
    result = add_user('', 'emptyuser@example.com', 'password123')
    assert result == False, "Добавление пользователя с пустым логином должно завершиться неудачей."

    result = add_user('emptyuser', '', 'password123')
    assert result == False, "Добавление пользователя с пустым email должно завершиться неудачей."

    result = add_user('emptyuser', 'emptyuser@example.com', '')
    assert result == False, "Добавление пользователя с пустым паролем должно завершиться неудачей."

def test_display_users_no_users(setup_database, connection):
    """Тест отображения списка пользователей при отсутствии зарегистрированных пользователей."""
    # Удаляем всех пользователей, если они есть
    cursor = connection.cursor()
    cursor.execute("DELETE FROM users;")
    
    users = display_users()  # Теперь функция возвращает список пользователей
    assert len(users) == 0, "Не должно отображаться пользователей, если они не зарегистрированы."

def test_user_choice_invalid_input(monkeypatch):
    """Тест функции user_choice для неверного ввода."""
    # Имитация неверного ввода
    monkeypatch.setattr('builtins.input', lambda _: '3')
    
    from io import StringIO
    import sys
    output = StringIO()
    sys.stdout = output

    choice = user_choice()
    assert choice == '3', "Должен быть возвращен неверный ввод '3'."
    assert "Неверный ввод" in output.getvalue(), "Должно быть выведено сообщение о неверном вводе."

    sys.stdout = sys.__stdout__  # Восстанавливаем стандартный вывод
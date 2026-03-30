import pytest
import sqlite3
from fastapi.testclient import TestClient
# Asegúrate de importar el módulo completo para poder parchearlo
import Seguro.FastAPI as FastAPI_module 
from Seguro.FastAPI import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db(monkeypatch): # Usamos la fixture monkeypatch de pytest
    """
    Configura una base de datos SQLite en memoria compartida.
    """
    # ✅ Usamos check_same_thread=False para los hilos de FastAPI
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Creamos la tabla
    cursor.execute("""
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT,
            email TEXT UNIQUE,
            password TEXT,
            edad INTEGER
        )
    """)

    # Insertamos usuario de prueba
    cursor.execute(
        "INSERT INTO users (nombre, email, password, edad) VALUES (?, ?, ?, ?)",
        ("Test User", "test@example.com", "password123", 30)
    )
    conn.commit()

    # ✅ SOBRESCRIBIMOS get_conn directamente en el módulo cargado
    # Esto garantiza que FastAPI use nuestra conexión en memoria
    monkeypatch.setattr(FastAPI_module, "get_conn", lambda: conn)

    yield conn
    conn.close()


# --- Tests de Endpoints ---

def test_login_exitoso():
    response = client.post("/login", params={"email": "test@example.com", "password": "password123"})
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["user"]["email"] == "test@example.com"


def test_login_fallido():
    response = client.post("/login", params={"email": "test@example.com", "password": "wrong_password"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Credenciales inválidas"


def test_registro_usuario_nuevo():
    payload = {
        "nombre": "Nuevo",
        "email": "nuevo@example.com",
        "password": "secure",
        "edad": 25
    }
    # FastAPI lee los argumentos de la función registro como query params según tu código
    response = client.post("/registro", params=payload)
    assert response.status_code == 200
    assert response.json()["nombre"] == "Nuevo"


def test_registro_edad_invalida():
    response = client.post("/registro", params={"nombre": "A", "email": "b@c.com", "password": "p", "edad": 150})
    assert response.status_code == 400
    assert "Edad no válida" in response.json()["detail"]


def test_get_usuario_existente():
    # El usuario insertado en la fixture tiene ID 1
    response = client.get("/usuario/1")
    assert response.status_code == 200
    assert response.json()["nombre"] == "Test User"


def test_get_usuario_no_existente():
    response = client.get("/usuario/999")
    assert response.status_code == 404


def test_delete_usuario():
    # Borramos al usuario 1
    response = client.delete("/usuario/1")
    assert response.status_code == 200
    assert response.json()["status"] == "eliminado"

    # Verificamos que ya no existe
    check = client.get("/usuario/1")
    assert check.status_code == 404

import sqlite3
import os
from fastapi import FastAPI, HTTPException

app = FastAPI()

# Configuración mediante variables de entorno
DB = os.getenv('DATABASE_NAME', 'usuarios.db')
SECRET = os.getenv('APP_SECRET_KEY', 'una-clave-muy-segura-y-larga')


def get_conn():
    conn = sqlite3.connect(DB)
    # Row permite acceder a los datos como un diccionario: user['email']
    conn.row_factory = sqlite3.Row
    return conn


@app.post('/login')
def login(email: str, password: str):
    conn = get_conn()
    cursor = conn.cursor()
    # ✅ SEGURO: Parámetros evitan Inyección SQL
    query = "SELECT nombre, email FROM users WHERE email=? AND password=?"
    cursor.execute(query, (email, password))
    user = cursor.fetchone()

    if user:
        return {'status': 'ok', 'user': dict(user)}
    raise HTTPException(status_code=401, detail="Credenciales inválidas")


@app.post('/registro')
def registro(nombre: str, email: str, password: str, edad: int):
    # ✅ SEGURO: Validación básica y parámetros
    if edad < 0 or edad > 120:
        raise HTTPException(status_code=400, detail="Edad no válida")

    conn = get_conn()
    try:
        conn.execute(
            "INSERT INTO users (nombre, email, password, edad) VALUES (?, ?, ?, ?)",
            (nombre, email, password, edad)
        )
        conn.commit()
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El email ya existe")

    return {'status': 'registrado', 'nombre': nombre}


@app.get('/usuario/{id}')
def get_user(id: int):
    conn = get_conn()
    # ✅ SEGURO: Solo campos necesarios
    row = conn.execute('SELECT nombre, email, edad FROM users WHERE id=?', (id,)).fetchone()
    if row:
        return dict(row)
    raise HTTPException(status_code=404, detail="Usuario no encontrado")


@app.delete('/usuario/{id}')
def delete_user(id: int):
    conn = get_conn()
    # ✅ SEGURO: Verifica si existe antes de decir que lo borró
    cursor = conn.execute('DELETE FROM users WHERE id=?', (id,))
    conn.commit()

    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    return {'status': 'eliminado', 'id': id}

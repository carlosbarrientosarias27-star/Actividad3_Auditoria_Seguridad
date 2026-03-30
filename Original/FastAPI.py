# api_usuarios.py  — CÓDIGO VULNERABLE (solo para ejercicio)

from fastapi import FastAPI
import sqlite3
import os

app = FastAPI()

DB = 'usuarios.db'
SECRET = 'clave123'  # ← hardcoded

def get_conn():
    return sqlite3.connect(DB)

# ENDPOINT 1: Login
@app.post('/login')
def login(email: str, password: str):
    conn = get_conn()
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE email='{email}' AND password='{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    if user:
        return {'status': 'ok', 'user': user}  # devuelve fila completa con hash
    return {'status': 'error'}

# ENDPOINT 2: Registro
@app.post('/registro')
def registro(nombre: str, email: str, password: str, edad: int):
    conn = get_conn()
    conn.execute(
        f"INSERT INTO users VALUES ('{nombre}', '{email}', '{password}', {edad})"
    )  # ← sin validaciones de edad ni formato
    conn.commit()
    return {'ok': True}

# ENDPOINT 3: Obtener usuario (sin autenticación)
@app.get('/usuario/{id}')
def get_user(id: int):
    conn = get_conn()
    row = conn.execute(f'SELECT * FROM users WHERE id={id}').fetchone()
    return row  # expone todos los campos incluyendo password

# ENDPOINT 4: Eliminar (sin verificar permisos)
@app.delete('/usuario/{id}')
def delete_user(id: int):
    conn = get_conn()
    conn.execute(f'DELETE FROM users WHERE id={id}')
    conn.commit()
    return {'deleted': id}
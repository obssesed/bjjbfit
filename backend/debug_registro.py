import requests
import json

url = "http://localhost:8000/api/deportistas/"
data = {
    "username": "debug_user_final",
    "email": "debug@test.com",
    "password": "password123",
    "first_name": "Debug",
    "last_name": "User",
    "nif": "12345678Q",
    "sexo": "M",
    "fecha_nacimiento": "1990-01-01",
    "telefono": "666777888",
    "cuenta_bancaria": "ES00112233"
}

try:
    print(f"Enviando petición a {url}...")
    response = requests.post(url, json=data)
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error de conexión: {e}")

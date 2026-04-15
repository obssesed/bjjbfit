# Bjjbfit - Plataforma de Reservas

Este es el repositorio principal para la aplicación web de gestión de reservas de clases de Brazilian Jiu-Jitsu.
La arquitectura empleada es desacoplada: utiliza **Django REST Framework (DRF)** como backend y **Angular** como frontend.

## Estructura del Proyecto

El proyecto está diseñado pensando en separar las responsabilidades de forma clara:
* `/backend/`: Contiene el core de Python y el servidor Django que gestionará la base de datos (PostgreSQL) y la API REST.
* `/frontend/`: Contiene la SPA (Single Page Application) desarrollada en Angular.
* `/venv/`: Entorno virtual de Python aislado para el backend (no se incluye en control de versiones).

## Guía de Ejecución Local

### 1. Iniciar el Backend (Django)
Abre una terminal dedicada para el backend. Desde la raíz de este proyecto (`/bjjfit`), asegúrate de tener el entorno virtual activado y arranca el servidor:

```powershell
# 1. Activar el entorno virtual (si no lo está ya)
.\venv\Scripts\Activate.ps1

# 2. Navegar a la carpeta del servidor
cd backend

# 3. Aplicar migraciones iniciales de la base de datos
python manage.py migrate

# 4. Arrancar el servidor
python manage.py runserver
```
El panel de API estará disponible en `http://localhost:8000/`.

### 2. Iniciar el Frontend (Angular)
Abre otra terminal simultánea dedicada para el frontend.

```powershell
# 1. Navegar a la carpeta frontend
cd frontend

# 2. Arrancar el servidor de desarrollo de Angular
npm start
# o
npx ng serve
```
La aplicación será accesible desde tu navegador web en `http://localhost:4200/`.

---
## Estándares de Código
Para cumplir con los estándares `Project Phoenix`:
* **Idiomas**: Modelos, variables, docstrings en Español. Todo lo técnico/librerías en Inglés.
* **Docstrings**: Formato Google exhaustivo, documentando los parámetros de entrada y salida para facilitar que cualquier miembro asuma el mantenimiento del código.

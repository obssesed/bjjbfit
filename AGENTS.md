# Project Phoenix - AI General Guidelines

Este documento centraliza las reglas generales del asistente de IA para Project Bjjfit.

## 🤖 Rol y Perfil

Eres un experto en Python (3.14+) y Angular enfocado en arquitectura escalable.

## 📜 Estándares Globales

### Lenguaje y Nomenclatura

- **Español**: Nombres de variables, modelos, funciones y docstrings (formato Google) para lógica de dominio.
- **Inglés**: Keywords, nombres de librerías y términos técnicos puros.

### Arquitectura (Fat Models / Skinny Views)

- **Modelos/Servicios**: La lógica de negocio debe residir en modelos o capas de servicio. Mantén las vistas ligeras.
- **ORM (Crítico)**: Optimización por defecto. Usa `select_related` y `prefetch_related`. Evita consultas N+1 en cada operación.
- **Vistas**: Usa Class-Based Views (CBVs) por defecto.

## 🏗️ Arquitectura de Vistas

- **API Vistas**: Usa Django REST Framework (DRF). Predominantemente `ModelViewSet` o `GenericAPIView` para el desarrollo ágil de la API.
- **Permisos**: Usa clases de permisos propias de DRF como `IsAuthenticated` para proteger los endpoints.

## 🛠️ Stack Tecnológico

- **Core**: Backend en Python (Django + Django REST Framework) y Frontend en Angular.
- **BD**: PostgreSQL (Sistema de base de datos relacional robusto para producción).

## ⚠️ Error Handling y Validación

- Usa bloques `try-except` claros en vistas y lógica de negocio.

## 📂 Estructura de Contexto Contextual

El comportamiento del agente se especializa según el directorio:

- Consultar obligatoriamente `AGENTS.md`.
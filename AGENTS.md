# Project    - AI General Guidelines

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

## ⚠️ Error Handling, Testing y Validación

- Usa bloques `try-except` claros en vistas y lógica de negocio.
- **Norma Estricta (TDD)**: Cualquier nueva funcionalidad, validador o campo añadido al Backend *requiere imperativamente* la creación inmediata de su respectivo Test Automático en Pytest antes de dar por completado el ticket. No se admiten desarrollos backend en BJJFIT sin su red de escaneo de Pytest (Casos OK y KO).

## 📂 Estructura de Contexto Contextual

El comportamiento del agente se especializa según el directorio:

- Consultar obligatoriamente `AGENTS.md`.

## Proyecto BJJBFIT e ideas de negocio
# 🧩 1. Resumen del negocio

Aplicación web para la gestión de reservas de clases de un gimnasio de Brazilian Jiu-Jitsu, con:

- Gestión de alumnos (adultos y niños)
- Sistema de reservas de clases con aforo
- Lista de espera
- Control de asistencia
- Gestión de planes mensuales (incluyendo familiares)
- Panel administrativo desde la interfaz UI con métricas y reporting
- Notificaciones push a usuarios desde la webapp una vez logueados

**Escala aproximada:**
- ~300 alumnos actuales (máx. esperado: 450)

---

# 👥 2. Usuarios y roles

## 2.1 Tipos de usuarios

### Alumno

Subtipos:
- Adulto / Adulto Familiar (adulto que gestiona niños)
- Niño
- Juvenil (14-17 años)

Capacidades:
- Login
- Reservar clases
- Cancelar reservas
- Ver historial de clases

---

### Adulto con niños (caso especial)

- Puede tener uno o varios perfiles de niños asociados
- Puede:
  - Reservar clases para los niños
  - Reservar para sí mismo

**Implicación técnica:**
- Relación padre → hijos (1:N)
- Gestión de permisos delegados

---

### Profesor

---

### Administrador / Profesor

- 1 único admin y perfil de profesor

Capacidades:

- Puede crear/editar clases
- Puede propagar clases en el tiempo
- Gestión de usuarios
- Activar planes
- Ver métricas
- Ver cancelaciones
- Puede definir y asignar los bonos(planes) activos que tienen los deportistas, ejemplo:
  - Mensual: clases ilimitadas al mes
  - Bono Familiar mensual: clases ilimitadas al mes y con 50 % de descuento para ambos familiares

---

# 📅 3. Gestión de clases

## 3.1 Creación de clases

- Las puede crear el admin / profesor
- Se pueden propagar en rangos de fechas (ej: repetir semanalmente)

## 3.2 Configuración de clases

- Aforo configurable (decidido por admin)
- Tipo de clases con su titulo, descripcion etc.

---

# 📌 4. Sistema de reservas

## 4.1 Reserva

- El alumno puede:
  - Reservar clases
  - Reservar múltiples clases al día

- Antelación:
  - Hasta 1 día antes
  - También último minuto

---

## 4.2 Cancelación

- Permitida hasta 30 minutos antes

---

## 4.3 Clases llenas

- Existe lista de espera
- Automática, si un deportista cancela en tiempo, el sistema deja entrar al siguiente de la lista de espera y le notifica (push) de que ha entrado.

---

## 4.5 Niños

- Niños sin restriccion para reservar clases o cancelarlas, el adulto que esta a su cargo tambien puede reservar clases del perfil del niño sin ningun tipo de restricción

---

# 📏 5. Reglas de negocio

## Confirmadas

- Aforo máximo por clase
- Lista de espera
- Cancelación hasta 30 min antes
- Reservas múltiples por día permitidas
- Plan debe estar activado por admin

---

# 💳 6. Planes y membresías

## Tipos

- Plan mensual
- Plan familiar (con descuento)

## Funcionamiento

- El admin activa manualmente el plan, una vez activado el plan el usuario puede entrar con sus credenciales a la webapp y poder reservar las clases y hacer uso de todas las funcionalidades que le son permitidas, y no antes.

---

# 🔔 7. Notificaciones

- Confirmación de reserva
- Confirmación de cancelación
- Aviso al admin cuando alguien cancela.
- Aviso desde lista de espera
- Recordatorio antes de clase
- Push notifications

---

# 📊 8. Reporting y administración

## Métricas

- Altas del mes
- Bajas del mes
- Asistencia:
  - Por actividad
  - Por franja horaria
  - Por género
  - Por edad

## Listados

- Exportables con filtros
- Datos completos de usuario

## Historial

- Hasta 3 años
- Desglosado por semanas, seleccionable la semana que se quiera ver.

---

# 👤 9. Modelo de usuario

## Campos obligatorios

- Nombre
- Apellidos
- NIF/DNI
- ID interno (modificable)
- Teléfono
- Email
- Sexo
- Fecha de nacimiento

## Campos opcionales

- Cinturón del atleta(solo lo ve el admin). Por defecto una vez se ha dado de alta por primera vez y activado el bono del atleta, este será cinturón blanco.
- Grados del atleta (solo lo ve el admin)
- Cuenta bancaria

---

# 🔗 10. Relaciones importantes

- Adulto → Niños (1:N)
- Usuario → Reservas (1:N)
- Clase → Reservas (1:N)
- Clase → Lista de espera

---

# 🔄 11. Migración e integración

- Existe base de datos actual
- Se requiere:
  - Importación de usuarios
  - Migración de datos históricos

---

# ⚙️ 12. Requisitos no funcionales

- Usuarios: hasta ~450
- Idiomas:
  - Español
- UI:
  - Ágil
  - Visual
  - Moderna
- Legal:
  - Protección de datos (footer)

---

# 🎥 13. Extras / funcionalidades adicionales

- Sección de vídeo semanal
  - Para repaso de clases

---


# 🧱 15. MVP sugerido

## MVP

- Gestión de usuarios
- Relación adulto → niños
- Gestión de clases (CRUD + propagación)
- Reservas
- Cancelaciones
- Lista de espera básica
- Notificaciones básicas
- Panel admin simple

---

## Fase 2

- Reporting avanzado
- Vídeos
- Penalizaciones
- Automatizaciones complejas
- Integraciones externas

---

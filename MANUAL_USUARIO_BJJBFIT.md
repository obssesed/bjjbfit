# 🥋 MANUAL DE USUARIO - BJJBFIT
**Plataforma de Gestión Integral para Academias de BJJ**

---

## 1. Introducción
Bienvenido a **BJJBFIT**, tu ecosistema digital diseñado específicamente para la gestión de academias de Brazilian Jiu-Jitsu. Esta plataforma centraliza el control de alumnos, reservas, graduaciones y finanzas en una interfaz moderna y ágil.

---

## 2. Perfil del Administrador (Backoffice)
El panel de administración es el centro de control del gimnasio. Aquí podrás gestionar todo lo necesario para el funcionamiento diario.

### 2.1 Gestión de Deportistas
Desde el menú "Usuarios", puedes visualizar tres estados principales:
*   **Activos**: Alumnos con un plan de pago vigente.
*   **Pendientes**: Nuevos registros que esperan a que les asignes un plan y cinturón.
*   **Inactivos/Bajas**: Histórico de alumnos que ya no entrenan.

**Acciones disponibles por alumno:**
*   **Asignar Nº Socio**: Edición rápida del ID interno.
*   **Cambio de Plan**: Modificar la tarifa (Mensual, Familiar, etc.).
*   **Graduación**: Subir de cinturón o añadir "grados" (rayas/esparadrapos) visuales. El sistema guarda automáticamente la fecha del último ascenso.
*   **Gestión de Pagos**: Configurar si el alumno paga en efectivo o mediante cuenta bancaria (IBAN).
*   **Paginación**: La lista de activos está organizada en páginas de 10 alumnos para facilitar la navegación en academias grandes.

### 2.2 Programación de Clases
En el panel de "Programación", puedes definir el horario del tatami:
*   **Plantillas**: Crea modelos de clase (ej: "BJJ Fundamentos", "No-Gi Avanzado") con su icono, duración y aforo.
*   **Propagación**: Selecciona una plantilla y "lánzala" al calendario en un rango de fechas (ej: todos los Lunes y Miércoles de este mes).
*   **Clases Puntuales**: Añade sesiones únicas en días específicos desde el calendario interactivo.

### 2.3 Sistema de Aforos y Lista de Espera
El sistema es **autónomo**:
1.  Si una clase llega a su límite, los siguientes alumnos entran en **Lista de Espera**.
2.  Si un alumno confirmado cancela su plaza, el sistema **asciende automáticamente** al primer alumno en espera y le notifica.

### 2.4 Reportes y Métricas
Obtén una visión clara de la salud de tu negocio:
*   **Estimación de Ingresos**: Cálculo en tiempo real de lo que deberías recaudar según los planes activos.
*   **Distribución por Cinturón**: Gráfica del nivel técnico de la academia.
*   **Métricas de Género y Edad**: Estadísticas demográficas de tus alumnos.

---

## 3. Perfil del Alumno (App)
La experiencia del alumno está optimizada para el uso en el móvil desde el vestuario.

### 3.1 Reservas y Calendario
*   **Reserva rápida**: Selecciona un día en el calendario y pulsa "Reservar".
*   **Gestión Familiar**: Si un padre tiene hijos registrados a su cargo, podrá elegir si la reserva es para él mismo o para uno de sus hijos sin cambiar de cuenta.
*   **Regla de Cancelación**: Se permite cancelar hasta **30 minutos antes** de la clase. Pasado ese tiempo, la plaza queda bloqueada para asegurar el orden del tatami.

### 3.2 Mi Perfil y Progresión
*   **Cinturón Virtual**: El alumno ve su rango actual y cuántos grados tiene acumulados.
*   **Historial**: Listado detallado de las clases asistidas y su frecuencia por tipo de actividad.

### 3.3 Vídeos de Repaso
Acceso exclusivo a la sección de "Vídeo Semanal", donde el profesor sube las técnicas trabajadas para que el alumno pueda repasarlas desde casa.

---

## 4. Preguntas Frecuentes (FAQ)

**¿Qué pasa si un alumno no tiene plan activo?**
El sistema le impedirá realizar reservas. El administrador debe aprobar su alta y asignarle un plan desde el panel de usuarios.

**¿Cómo funcionan los planes familiares?**
Al activar un plan como "Familiar", el sistema aplica automáticamente el descuento configurado (ej: 50%) tanto al titular como a sus familiares asociados.

**¿Puedo limitar quién ve qué clases?**
Sí. Al crear una plantilla, puedes definir la "Categoría de Acceso" (Adulto, Juvenil o Infantil). El sistema filtrará automáticamente las clases para que cada alumno solo vea las que le corresponden por edad.

---

## 5. Soporte Técnico
Para incidencias críticas o dudas sobre el despliegue:
*   **Acceso**: [URL_DE_TU_ACADEMIA]
*   **Tecnología**: Stack Angular + Django REST.

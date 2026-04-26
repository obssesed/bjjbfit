# ESTADO DEL ARTE - PROYECTO BJJFIT
**Fecha**: Abril 2026

## 1. Resumen Ejecutivo
Nos encontramos en un estado avanzado de cumplimiento del MVP (Producto Mínimo Viable) propuesto en los requerimientos originales. El núcleo transaccional (**reservas y aforos**) es funcional y ha sido blindado (100% de cobertura en tests en endpoints críticos). El ecosistema Frontend respira un diseño ultra-premium y la experiencia de usuario (UI Gamificada) aporta mucho valor de fidelización.

---

## 2. Hitos Alcanzados (Lógica de Negocio y Producto)

### 2.1 Ecosistema de Usuarios y Roles
- **Delegación Familiar Activa**: Los usuarios Adultos pueden tener hijos tutelados (`padre_tutor`). Pueden reservar la participación de sus pequeños en las clases sin que el menor necesite correo o login.
- **Jerarquía Administrativa**: Panel de profesor habilitado usando Django Admin, que actúa como fuente de la verdad para modificar variables directas (nombres, planes o subir grados de BJJ).
- **Gamificación**: El Modelo de deportistas integra la progresión de cinturones reales de BJJ (Adultos e Infantiles) y grados de 0 a 4. Todo se dibuja en frontend como esparadrapo virtual envuelto, sumado a un autotrackeo de la *Última Fecha de Graduación* generado por un "override" silencioso en el guardado de Base de Datos, sin que el profesor deba escribir fechas a mano.

### 2.2 Sistema Transaccional de Aforos
- **Listas de Espera Autónomas**: Las clases controlan su `capacidad_maxima`. Si un deportista intenta reservar cuando la clase está llena, el Serializador de Django lo inscribe en estado `ESPERA`.
- **Soft-Delete y Ascenso Automático**: Si un deportista anula su confirmación, en lugar de borrar su reserva de la DB, ésta pasa a `CANCELADA`. Automáticamente, el sistema promociona a la persona más antigua de la Lista de Espera a `CONFIRMADA`.

### 2.3 Seguridad y Reglas Core en API (Hardening)
1. **Regla del Plan**: Sólo se puede reservar si el profesor marcó `plan_activo=True` a una cuenta.
2. **Regla Cronológica de Registro**: Es imposible reservar clases que ya sucedieron en el pasado (Bloqueo backend anti-hacks).
3. **Regla Cronológica de Cancelación**: No se permite cancelar y perder la plaza a menos de 30 minutos de distancia del evento, salvaguardando el ecosistema y la lista de espera.
4. **Anti-Spam**: Protecciones estrictas contra la duplicidad de reservas en la misma clase para un mismo individuo.

---

## 3. Hoja de Ruta Pendiente (Next Steps)

Para que el Producto Mínimo Viable salga a colapsar el mercado, necesitamos enfocarnos en los siguientes aspectos faltantes de la toma de requisitos original e ideas futuras:

### Fase 1 (Cierre del MVP Core)
- **Selector Infantil en UI de Reservas**: Actualmente, el Backend API permite que un padre reserve pasándole por JSON la `ID` del hijo. En el panel Angular, al pulsar "Reservar", debemos dar la opción visual (un desplegable o radio buttons) que pregunte: *"¿Reservas plaza para Ti o para [Nombre del Hijo]?"*.
- **Lista de Asistencia "In Situ" del Profesor**: Una vista exclusiva donde el Profesor/Admin (logueado en Frontend) pase lista fácilmente a los apuntados el día y hora de la clase.
- **Sistema de Reembolso/Penalizaciones (Opcional MVP)**: ¿Si la falta no está justificada y el profesor le marca como 'No asistió', penalizar su reserva futura o descontar pases limitados? 

### Fase 2 (Post-MVP y Features Adicionales)
- **Panel Administrativo Nativo Angular**: Desvincular al gerente de tocar el *Django Admin* y ofrecerle un panel visual para aprobar Altas, Bajas, Activar mensualidades familiares y Subir grados/cinturones directamente observando fotos de los deportistas.
- **Dashboard de Reporting Avanzado (Métricas)**: Generar un endpoint que analice el uso del tatami. Gráficas semanales de género, cinturón, aforos más pico y porcentaje de cancelaciones, lo cual ayuda en el negocio a prever picos horarios y altas del mes.
- **Sistema de Notificaciones Push/Mail**: Automatizar un *Celery Task* o usar Firebase para enviar avisos reales cuando un usuario de lista de espera entra de forma sorpresiva en la ventana de participación.
- **Bóveda de Video Semanal**: Un micro-portal dentro de BJJFIT que permita insertar un enlace privado de Youtube con técnicas repasadas esa semana, de acceso exclusivo a los que tienen `plan_activo=True`.

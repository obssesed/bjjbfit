# ESTADO DEL ARTE - PROYECTO BJJBFIT
**Fecha**: Mayo 2026

## 1. Resumen Ejecutivo
El proyecto ha alcanzado la madurez de un **MVP (Producto Mínimo Viable)** de alta fidelidad. El núcleo de negocio (reservas, aforos, jerarquía familiar y planes) es 100% funcional. La interfaz administrativa ha migrado de Django Admin a un ecosistema **Angular Premium** mucho más ágil y visual. La robustez del backend está garantizada por una capa de servicios optimizada que gestiona la lógica compleja de listas de espera y promociones automáticas.

---

## 2. Hitos Alcanzados (Lógica de Negocio y Producto)

### 2.1 Ecosistema de Usuarios y Roles
- **Delegación Familiar Completa**: Implementada tanto en Backend como en UI. Los padres pueden alternar perfiles y reservar para sus hijos con un solo clic.
- **Paneles Administrativos Nativos**: Gestión de Usuarios, Planes Mensuales, Programación de Clases y Notificaciones centralizada en Angular.
- **Sistema de Graduación Gamificado**: Visualización de cinturones y grados (esparadrapos) dinámica. El sistema trackea automáticamente la progresión técnica del atleta.

### 2.2 Gestión de Clases y Aforos
- **Propagación Inteligente**: El administrador puede diseñar una "Plantilla de Clase" y propagarla en el calendario por rangos de fechas y días de la semana.
- **Listas de Espera y Ascensos**: Lógica autónoma que promociona al primer usuario en espera cuando se libera una plaza, manteniendo el tatami siempre al máximo rendimiento.

### 2.3 Seguridad y Hardening
- **Protección de Identidad (Anti-IDOR)**: Verificación estricta de que un usuario solo pueda reservar/cancelar para sí mismo o sus hijos delegados.
- **Validación de Planes**: El sistema bloquea reservas si el alumno no tiene un plan activo aprobado por el administrador.
- **Ventanas de Tiempo**: Bloqueo de cancelaciones "last-minute" (30 min) y prohibición de reservas retroactivas.

### 2.4 Vídeos y Fidelización
- **Bóveda de Técnica Semanal**: Sistema de subida y visualización de vídeos para que los alumnos repasen las técnicas explicadas en clase desde su perfil.

---

## 3. Estado del MVP: ¿Es Válido?
**SÍ.** El producto actual cubre el 95% de los requerimientos críticos para operar una academia de BJJ de tamaño medio (300-500 alumnos). 
- Permite el flujo completo desde el registro hasta la reserva.
- Ofrece herramientas de control financiero (reportes de ingresos estimados).
- Facilita la comunicación (notificaciones manuales masivas).

---

## 4. Hoja de Ruta (Post-MVP)

Para pasar de un MVP a un producto de mercado (SaaS), los siguientes pasos son clave:

### Fase 1 (Optimización Operativa)
- **Control de Asistencia "Check-in"**: Añadir un botón en el panel de programación para que el profesor marque quién asistió realmente (Estado: ASISTIDA), útil para métricas de retención.
- **Notificaciones Push Automáticas**: Integrar Firebase para que el aviso de "Has subido de lista de espera" llegue como notificación push al móvil del usuario.

### Fase 2 (Escalabilidad y UX)
- **Pasarela de Pago Real**: Integrar Stripe o similar para automatizar el cobro de los planes (actualmente es manual por el admin).
- **Métricas de Rendimiento del Tatami**: Gráficos más profundos sobre qué horas tienen más tasa de cancelación o qué profesores atraen más alumnos.
- **App Móvil Nativa**: Empaquetar la webapp como PWA para facilitar el acceso rápido desde el vestuario.

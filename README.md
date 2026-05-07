# Autorización de Compras (Purchase Authorization)

Módulo para Odoo 19.0 que agrega un flujo de autorización a las órdenes de compra (OC). Permite solicitar aprobación a usuarios específicos antes de confirmar una orden, con notificaciones mediante actividades y el chatter de Odoo.

---

## Funcionalidad

### 1. Campo en Usuarios (`res.users`)

Se agrega el campo booleano **"Puede Autorizar Compras"** en la pestaña *Derechos de Acceso* del formulario de usuario.

- Solo los usuarios con este check activado recibirán las solicitudes de autorización.
- Al activar el check, el usuario se agrega automáticamente al grupo *Gestor de Autorización*.
- Al desactivarlo, se remueve del grupo automáticamente.

### 2. Flujo de Autorización en Órdenes de Compra

El módulo agrega los siguientes campos al modelo `purchase.order`:

| Campo | Tipo | Descripción |
|---|---|---|
| `authorization_state` | Selección | Estado actual: Borrador / Autorización Solicitada / Autorizado / Rechazado |
| `authorization_requested_by` | Many2one (Usuario) | Quién solicitó la autorización |
| `authorization_date` | Datetime | Fecha en que se autorizó |
| `authorized_by` | Many2one (Usuario) | Quién autorizó o rechazó |
| `rejection_reason` | HTML | Motivo de rechazo (si aplica) |

#### Botones en el Header

- **Solicitar Autorización** — Visible cuando la OC está en estado *Borrador*. Cambia el estado a *Autorización Solicitada*.
- **Autorizar** — Visible solo para usuarios del grupo *Gestor de Autorización* cuando el estado es *Autorización Solicitada*. Aprueba la orden, marca las actividades como hechas y confirma la OC automáticamente.
- **Rechazar** — Visible solo para usuarios del grupo *Gestor de Autorización* cuando el estado es *Autorización Solicitada*. Abre un asistente para ingresar el motivo y rechaza la orden.

#### Comportamiento de Botones Nativos

Cuando una orden tiene autorización solicitada o está rechazada, los botones nativos de Odoo (*Confirmar*, *Enviar por Email*, etc.) se ocultan automáticamente para evitar acciones manuales durante el flujo de autorización.

### 3. Notificaciones

**Al solicitar autorización:**
1. Se crea una **Actividad** (Tarea pendiente) para cada usuario autorizador, visible en el menú *Actividades*.
2. Se envía una **notificación por chatter** a los autorizadores, que también se entrega por email según la configuración de preferencias de cada usuario.

**Al autorizar:**
1. Las actividades pendientes se marcan como *Hechas*.
2. Se registra una notificación en el chatter de la OC.

**Al rechazar:**
1. Las actividades pendientes se marcan como *Hechas*.
2. Se notifica al usuario que solicitó la autorización con el motivo de rechazo.

### 4. Pestaña de Autorización

En el formulario de la OC se agrega una pestaña **"Autorización"** que muestra:
- Estado actual (con badge)
- Quién solicitó
- Fecha de autorización
- Quién autorizó/rechazó
- Motivo de rechazo (solo visible si existe)

### 5. Vista de Lista

En la vista de árbol de órdenes de compra se agrega la columna **"Estado de Autorización"** para visualizar rápidamente el estado de cada orden.

---

## Seguridad

| Grupo | Descripción |
|---|---|
| Categoría *Autorización de Compras* | Categoría del módulo |
| *Gestor de Autorización* | Usuarios que pueden ver y usar los botones *Autorizar* y *Rechazar* |

El grupo *Gestor de Autorización* se asigna/remueve automáticamente al activar/desactivar el campo *Puede Autorizar Compras* en el usuario.

---

## Dependencias

- `purchase` — Módulo base de compras
- `mail` — Sistema de notificaciones y actividades

---

## Flujo Completo

```
1. OC en Borrador
       │
       ▼
2. Usuario da click en "Solicitar Autorización"
       │
       ▼
3. Estado → "Autorización Solicitada"
   Actividades creadas para autorizadores
   Notificación enviada
       │
       ├─────────────────────────────┐
       ▼                             ▼
4. Autorizar                    Rechazar
       │                             │
       ▼                             ▼
   Estado → "Autorizado"         Estado → "Rechazado"
   Actividades → Hechas          Actividades → Hechas
   OC → Confirmada               Se notifica al solicitante
```

---

## Autor

DGV

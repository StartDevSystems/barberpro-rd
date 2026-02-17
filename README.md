# BarberPro RD - SaaS para Barberías

BarberPro RD es una plataforma como servicio (SaaS) diseñada para modernizar la gestión de barberías, permitiendo el agendamiento de citas online, la administración de servicios y el seguimiento de ingresos.

## Arquitectura y Decisiones Técnicas

El proyecto está construido con Django, un framework de Python robusto y escalable, ideal para un desarrollo rápido y seguro.

### Stack Tecnológico
- **Backend**: Python, Django, Django REST Framework
- **Base de Datos**: SQLite (para desarrollo), preparado para migrar a PostgreSQL en producción.
- **Frontend**: Django Templates con Bootstrap 5 (Mobile-First).

### Diseño Multi-Tenant

Aunque la primera versión operará con una sola barbería, la arquitectura está diseñada para ser **Multi-Tenant**. Esto significa que múltiples barberías podrán usar la misma instancia de la aplicación en el futuro, manteniendo sus datos completamente aislados.

El modelo `BarberShop` es el ancla principal. Todos los demás modelos de negocio (`Service`, `Client`, `Appointment`) tienen una relación directa (ForeignKey) con `BarberShop`. Esto garantiza que cada dato pertenece a una y solo una barbería, sentando las bases para una futura separación lógica de datos a nivel de aplicación.

---

## FASE 1: Setup del Proyecto (Completada)

En esta fase se ha configurado la estructura inicial del proyecto, la base de datos y el panel de administración.

### Estructura de Carpetas

```
E:\App_Barber_Shop
├── .venv/                  # Entorno virtual de Python
├── barberpro/              # Directorio de configuración del proyecto Django
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py         # Archivo de configuración principal
│   ├── urls.py             # URLs a nivel de proyecto
│   └── wsgi.py
├── scheduling/             # Aplicación principal de Django ("core")
│   ├── migrations/         # Migraciones de la base de datos
│   ├── __init__.py
│   ├── admin.py            # Configuración del panel de admin
│   ├── apps.py
│   ├── models.py           # Modelos de datos (esquema de la DB)
│   ├── tests.py
│   └── views.py
├── manage.py               # Utilidad de línea de comandos de Django
└── db.sqlite3              # Base de datos (desarrollo)
```

### Pasos Realizados

1.  **Entorno Virtual**: Se creó un entorno virtual para aislar las dependencias (`.venv`).
2.  **Instalación de Django**: Se instalaron `django` y `djangorestframework`.
3.  **Creación del Proyecto**: Se inicializó el proyecto Django (`barberpro`).
4.  **Creación de la App**: Se creó la aplicación `scheduling` para manejar la lógica de negocio.
5.  **Definición de Modelos**: Se definieron los modelos `BarberShop`, `Service`, `Client` y `Appointment` en `scheduling/models.py`.
6.  **Migraciones**: Se crearon y aplicaron las migraciones para estructurar la base de datos SQLite.
7.  **Panel de Administración**: Se registraron los modelos en `scheduling/admin.py` para permitir la gestión de datos a través del admin de Django.

### Cómo Ejecutar el Proyecto

1.  **Asegúrate de haber creado un superusuario** con el comando:
    ```bash
    # En Windows (desde la raíz del proyecto)
    .\.venv\Scripts\python.exe manage.py createsuperuser
    ```

2.  **Inicia el servidor de desarrollo**:
    ```bash
    .\.venv\Scripts\python.exe manage.py runserver
    ```

3.  **Accede al Panel de Administración**:
    - Abre tu navegador y ve a `http://127.0.0.1:8000/admin/`.
    - Inicia sesión con las credenciales del superusuario que creaste.
    - Ahora puedes crear tu primera `BarberShop` y ver los demás modelos listos para ser gestionados.

---

## FASE 2: Panel de Administración (Completada)

En esta fase se construyó la interfaz de administración interna que permite la gestión completa de los recursos de la barbería.

### Funcionalidades Implementadas

1.  **CRUD de Servicios**:
    - **Ruta**: `/app/services/`
    - Interfaz completa para listar, crear, editar y eliminar los servicios que ofrece la barbería.

2.  **CRUD de Clientes**:
    - **Ruta**: `/app/clients/`
    - Interfaz completa para gestionar la base de datos de clientes.

3.  **Gestión de Citas Manuales**:
    - **Ruta**: `/app/appointments/`
    - Permite agendar, ver y editar citas manualmente.

### Lógica de Validación de Disponibilidad

La funcionalidad más importante de esta fase es la validación de citas para evitar el *overbooking*. La lógica se implementó en `scheduling/forms.py` dentro del método `clean` del formulario `AppointmentForm`.

El sistema verifica que una nueva cita (o una cita que se está actualizando) no se solape con ninguna cita existente. La validación sigue estos pasos:
1.  Obtiene la fecha, hora de inicio y servicio de la cita propuesta.
2.  Calcula la hora de finalización sumando la `duration_minutes` del servicio a la hora de inicio.
3.  Busca en la base de datos todas las citas `pendientes` para la misma barbería en la misma fecha.
4.  Compara el intervalo de tiempo de la nueva cita (`inicio_nueva` a `fin_nueva`) con el intervalo de cada cita existente (`inicio_existente` a `fin_existente`).
5.  Si se cumple la condición de solapamiento (`inicio_nueva < fin_existente` y `fin_nueva > inicio_existente`), el formulario lanza un error de validación claro y descriptivo, impidiendo que la cita se guarde.

Este mecanismo garantiza la integridad de la agenda de la barbería.


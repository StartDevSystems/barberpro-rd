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

---

## FASE 3: Vista Pública para Clientes (Completada)

En esta fase se desarrolló la interfaz pública que permite a los clientes finales agendar sus citas de forma autónoma.

### Flujo de Agendamiento Público

El proceso para el cliente es el siguiente:

1.  **Página de Inicio (`/`)**: El cliente ve una lista de todos los servicios ofrecidos por la barbería, con sus precios y duraciones.
2.  **Selección de Servicio**: El cliente hace clic en el servicio que desea.
3.  **Asistente de Reserva (`/book/service/<id>/`)**: Se le presenta un formulario en varios pasos:
    *   **Paso 1: Elegir Fecha**: El cliente selecciona el día en que desea la cita.
    *   **Paso 2: Elegir Hora**: Al elegir una fecha, se hace una llamada a una API interna (`/api/available-slots/`) que calcula y devuelve las horas disponibles para ese día, considerando la duración del servicio y las citas ya agendadas. Las horas se muestran como botones clickeables.
    *   **Paso 3: Ingresar Datos**: El cliente introduce su nombre y número de teléfono.
4.  **Creación de la Cita**: Al enviar el formulario, el sistema:
    *   Valida los datos.
    *   Busca si el cliente ya existe por su número de teléfono. Si no, lo crea.
    *   Crea la `Appointment` con estado "Pendiente".
5.  **Página de Confirmación (`/booking/confirmation/<id>/`)**: Se redirige al cliente a una página que confirma todos los detalles de su cita recién creada.

### API de Disponibilidad

El endpoint en `/api/available-slots/` es el cerebro de la disponibilidad. Recibe una `fecha` y un `service_id` y realiza los siguientes cálculos:
- Define un horario laboral (ej: 9:00 a 18:00).
- Genera todos los posibles intervalos de tiempo de inicio (ej: cada 30 minutos).
- Consulta la base de datos para encontrar todas las citas ya agendadas para ese día.
- Filtra los intervalos de tiempo, eliminando aquellos que se solapan con citas existentes, asegurando que no haya overbooking.
- Devuelve una lista en formato JSON con las horas de inicio que están 100% disponibles.
Este enfoque dinámico asegura que el cliente siempre vea un calendario preciso.

---

## FASE 4: Dashboard Administrativo (Completada)

En esta fase se ha creado un dashboard en la ruta `/app/dashboard/` para ofrecer una vista general del rendimiento del negocio. La vista `DashboardView` se encarga de realizar todas las agregaciones y cálculos necesarios.

### Componentes del Dashboard

1.  **Tarjetas de Ingresos**:
    *   Se muestran tres tarjetas de acceso rápido que totalizan los ingresos de las citas con estado "Completada" para: **Hoy**, **Esta Semana** y **Este Mes**.

2.  **Gráfico de Ingresos (Últimos 7 Días)**:
    *   Utilizando la librería **Chart.js**, se renderiza un gráfico de líneas que muestra la tendencia de ingresos durante la última semana. Esto permite una visualización rápida del rendimiento diario.

3.  **Ranking de Clientes**:
    *   Se muestra una lista con el **Top 5 de clientes** ordenados por el total de dinero gastado en citas completadas. Esto ayuda a identificar a los clientes más valiosos.

4.  **Próximas Citas**:
    *   Una tabla muestra las próximas 5 citas que están en estado "Pendiente", ordenadas por fecha y hora. Esto permite al personal de la barbería prepararse para los próximos clientes.


---

## FASE 5: Arquitectura Multi-Tenant (Plan de Escalado)

Esta fase es teórica y sirve como guía para convertir la aplicación actual en un verdadero SaaS (Software as a Service) capaz de servir a múltiples barberías.

El diseño inicial de la base de datos (donde cada modelo principal se vincula a `BarberShop`) fue la clave. Ahora, solo necesitamos modificar cómo la aplicación identifica qué barbería mostrar.

### Estrategia: Middleware y Subdominios

El enfoque más limpio y profesional es usar subdominios para cada barbería.
- **Barbería 1**: `juan-cuts.barberpro.com`
- **Barbería 2**: `the-flow.barberpro.com`
- **Página principal (para registrarse)**: `www.barberpro.com`

Un **Middleware** de Django nos ayudará a gestionar esto automáticamente.

#### 1. Ejemplo de Middleware

Crearíamos un archivo `scheduling/middleware.py`:

```python
# scheduling/middleware.py
from .models import BarberShop

class MultiTenantMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extraer el subdominio del host (ej: 'juan-cuts' de 'juan-cuts.barberpro.com')
        host = request.get_host()
        parts = host.split('.')
        
        subdomain = None
        if len(parts) > 2 and parts[0] != 'www':
            subdomain = parts[0]

        request.barbershop = None
        if subdomain:
            try:
                # Asumiendo que el modelo BarberShop tiene un campo 'subdomain'
                request.barbershop = BarberShop.objects.get(subdomain=subdomain)
            except BarberShop.DoesNotExist:
                pass # Manejar subdominio no encontrado

        response = self.get_response(request)
        return response
```
*Nota: Esto requeriría añadir un campo `subdomain = models.SlugField(unique=True)` al modelo `BarberShop`.*

Luego, registraríamos este middleware en `barberpro/settings.py`.

#### 2. Refactorización de Vistas

Con el middleware activo, `request.barbershop` estaría disponible en todas las vistas. Podríamos eliminar `get_barbershop()` y refactorizar las vistas así:

**Antes (con `get_barbershop`):**
```python
def get_barbershop():
    return BarberShop.objects.first()

class ServiceListView(ListView):
    def get_queryset(self):
        barbershop = get_barbershop()
        if barbershop:
            return Service.objects.filter(barbershop=barbershop)
        return Service.objects.none()
```

**Después (con middleware):**
```python
class ServiceListView(ListView):
    def get_queryset(self):
        # El middleware ya nos da la barbería actual
        if self.request.barbershop:
            return Service.objects.filter(barbershop=self.request.barbershop)
        return Service.objects.none()
```
Este cambio simple, replicado en todas las vistas, completaría la transición a una arquitectura multi-tenant, aislando los datos de cada cliente de forma segura.

---

## Roadmap para SaaS Comercial

Convertir este proyecto en un negocio real requiere varios pasos adicionales. Este es un posible roadmap:

### V1: Minimum Viable Product (MVP)

1.  **Registro de Usuarios y Barberías**:
    - Crear un flujo de registro donde un nuevo dueño de barbería pueda crear una cuenta, registrar su barbería y elegir un subdominio.
    - Usar una librería como `django-allauth` para gestionar el registro, inicio de sesión y recuperación de contraseña.

2.  **Gestión de Suscripciones**:
    - Integrar un sistema de pagos como **Stripe** usando `dj-stripe` para manejar planes de membresía (ej: mensual, anual).
    - El modelo `BarberShop` ya tiene un campo `subscription_plan` preparado para esto.
    - Proteger las vistas para que solo usuarios con una suscripción activa puedan acceder.

3.  **Base de Datos de Producción**:
    - Migrar de SQLite a **PostgreSQL**, una base de datos mucho más robusta y adecuada para producción.

4.  **Despliegue (Deploy)**:
    - Desplegar la aplicación en una plataforma como **Render**, **Heroku** o **DigitalOcean App Platform**.
    - Configurar el servidor de archivos estáticos (ej: Amazon S3) y el servidor de producción (Gunicorn).

### V2: Features Adicionales

- **Gestión de Barberos/Staff**: Permitir que el dueño de la barbería añada a sus empleados y asigne citas a barberos específicos.
- **Notificaciones**: Enviar recordatorios de citas por email o SMS a los clientes.
- **Roles y Permisos**: Distinguir entre roles de "Dueño" y "Empleado" en el panel de administración.
- **Dashboard Avanzado**: Más métricas, filtros por fecha, etc.
- **Personalización**: Permitir que cada barbería suba su logo y personalice los colores de su página pública.

### V3: Escalado y Marketing

- **Página de Marketing**: Construir una página de inicio (`www.barberpro.com`) que explique las características del servicio y capture nuevos clientes (dueños de barberías).
- **Dominio Personalizado**: Permitir que una barbería use su propio dominio (ej: `www.juancuts.com`) en lugar de un subdominio.
- **Optimización y Monitoreo**: Implementar herramientas de monitoreo de rendimiento y errores para asegurar la estabilidad de la plataforma.

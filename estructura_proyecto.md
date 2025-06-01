# Estructura Modular del Proyecto Django - Sistema de Gestión de Clubes

## Visión General de la Arquitectura

El proyecto sigue una arquitectura modular basada en Django, diseñada para maximizar la escalabilidad, mantenibilidad y adaptabilidad a diferentes tipos de clubes. La estructura se organiza en aplicaciones independientes pero interconectadas, cada una responsable de un dominio específico de la lógica de negocio.

## Estructura de Directorios

```
club_django_project/
│
├── club_core/                # Configuración principal del proyecto
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py           # Configuraciones globales
│   ├── urls.py               # URLs principales
│   └── wsgi.py
│
├── apps/                     # Directorio contenedor de aplicaciones modulares
│   ├── __init__.py
│   │
│   ├── common/               # Funcionalidades compartidas entre módulos
│   │   ├── __init__.py
│   │   ├── models.py         # Modelos base y abstractos
│   │   ├── utils.py          # Utilidades comunes
│   │   └── middleware.py     # Middleware personalizado
│   │
│   ├── recursos/             # Gestión de objetos y recursos del club
│   │   ├── __init__.py
│   │   ├── models.py         # Modelos para recursos (objetos, equipamiento)
│   │   ├── views.py          # Vistas para gestión de recursos
│   │   ├── forms.py          # Formularios para recursos
│   │   ├── urls.py           # URLs específicas de recursos
│   │   ├── admin.py          # Configuración de admin para recursos
│   │   └── api/              # API para recursos
│   │
│   ├── alquiler/             # Sistema de alquiler de recursos
│   │   ├── __init__.py
│   │   ├── models.py         # Modelos para alquileres y reservas
│   │   ├── views.py          # Vistas para gestión de alquileres
│   │   ├── forms.py          # Formularios para alquileres
│   │   ├── urls.py           # URLs específicas de alquileres
│   │   ├── admin.py          # Configuración de admin para alquileres
│   │   └── api/              # API para alquileres
│   │
│   ├── ventas/               # Sistema de venta de productos
│   │   ├── __init__.py
│   │   ├── models.py         # Modelos para ventas y productos
│   │   ├── views.py          # Vistas para gestión de ventas
│   │   ├── forms.py          # Formularios para ventas
│   │   ├── urls.py           # URLs específicas de ventas
│   │   ├── admin.py          # Configuración de admin para ventas
│   │   └── api/              # API para ventas
│   │
│   ├── clases/               # Gestión de clases y actividades
│   │   ├── __init__.py
│   │   ├── models.py         # Modelos para clases, horarios, instructores
│   │   ├── views.py          # Vistas para gestión de clases
│   │   ├── forms.py          # Formularios para clases
│   │   ├── urls.py           # URLs específicas de clases
│   │   ├── admin.py          # Configuración de admin para clases
│   │   └── api/              # API para clases
│   │
│   ├── socios/               # Gestión de socios y suscripciones
│   │   ├── __init__.py
│   │   ├── models.py         # Modelos para socios, suscripciones, pagos
│   │   ├── views.py          # Vistas para gestión de socios
│   │   ├── forms.py          # Formularios para socios
│   │   ├── urls.py           # URLs específicas de socios
│   │   ├── admin.py          # Configuración de admin para socios
│   │   └── api/              # API para socios
│   │
│   └── administracion/       # Funcionalidades administrativas del club
│       ├── __init__.py
│       ├── models.py         # Modelos para configuración y administración
│       ├── views.py          # Vistas para administración
│       ├── forms.py          # Formularios para administración
│       ├── urls.py           # URLs específicas de administración
│       ├── admin.py          # Configuración de admin para administración
│       └── api/              # API para administración
│
├── static/                   # Archivos estáticos (CSS, JS, imágenes)
│   ├── css/
│   ├── js/
│   └── img/
│
├── templates/                # Plantillas HTML
│   ├── base.html            # Plantilla base con Bootstrap 5
│   ├── common/              # Plantillas compartidas
│   ├── recursos/            # Plantillas específicas de recursos
│   ├── alquiler/            # Plantillas específicas de alquileres
│   ├── ventas/              # Plantillas específicas de ventas
│   ├── clases/              # Plantillas específicas de clases
│   ├── socios/              # Plantillas específicas de socios
│   └── administracion/      # Plantillas específicas de administración
│
├── media/                    # Archivos subidos por usuarios
│
├── docs/                     # Documentación del proyecto
│   ├── api/                 # Documentación de API
│   ├── user/                # Manual de usuario
│   └── legal/               # Documentos legales
│
├── manage.py                 # Script de gestión de Django
├── requirements.txt          # Dependencias del proyecto
└── .env                      # Variables de entorno (no versionado)
```

## Descripción de Módulos

### 1. Common (Común)
Contiene funcionalidades compartidas entre todos los módulos, como modelos base abstractos, utilidades, middleware personalizado y mixins. Este módulo proporciona la base para la consistencia y reutilización de código en todo el proyecto.

### 2. Recursos
Gestiona todos los objetos y recursos disponibles en el club (equipamiento deportivo, libros, herramientas, etc.). Incluye funcionalidades para:
- Registro y categorización de objetos
- Control de inventario
- Gestión de estado de los objetos
- Registro fotográfico y descripción
- Historial de uso y mantenimiento

### 3. Alquiler
Maneja el sistema de alquiler y reserva de recursos. Incluye:
- Reserva de objetos con selección de fechas
- Cálculo de tarifas
- Gestión de depósitos y fianzas
- Notificaciones de vencimiento
- Registro de devoluciones
- Penalizaciones por retrasos o daños

### 4. Ventas
Gestiona la venta de productos y servicios. Incluye:
- Catálogo de productos
- Gestión de precios y descuentos
- Carrito de compras
- Proceso de checkout
- Facturación electrónica
- Historial de compras

### 5. Clases
Administra las clases y actividades ofrecidas por el club. Incluye:
- Programación de clases (horarios, duración, capacidad)
- Asignación de instructores
- Sistema de inscripción
- Control de asistencia
- Evaluación y feedback
- Gestión de materiales

### 6. Socios
Gestiona los socios del club y sus suscripciones. Incluye:
- Registro de socios
- Tipos de membresías y planes
- Gestión de pagos y renovaciones
- Historial de actividades
- Perfiles de usuario
- Sistema de puntos o beneficios

### 7. Administración
Proporciona funcionalidades administrativas para la gestión del club. Incluye:
- Configuración general del club
- Informes y estadísticas
- Gestión financiera
- Administración de usuarios y permisos
- Configuración de políticas y reglas

## Interconexión entre Módulos

Los módulos están diseñados para funcionar de manera independiente pero interconectada:

1. **Recursos** proporciona la base de objetos que pueden ser alquilados o vendidos.
2. **Alquiler** y **Ventas** dependen de **Recursos** para acceder a los objetos disponibles.
3. **Clases** puede utilizar **Recursos** para asignar materiales necesarios.
4. **Socios** se conecta con todos los demás módulos para registrar actividades, compras y alquileres.
5. **Administración** proporciona una visión global y gestión de todos los módulos.

## Extensibilidad

La estructura modular permite:
- Añadir nuevos tipos de clubes sin modificar el código existente
- Extender funcionalidades específicas de cada módulo
- Personalizar la interfaz de usuario según el tipo de club
- Integrar con sistemas externos a través de APIs

## Configuración y Personalización

El sistema está diseñado para ser altamente configurable:
- Tipos de recursos personalizables
- Reglas de alquiler y venta configurables
- Tipos de clases y actividades adaptables
- Planes de suscripción personalizables
- Políticas y reglas ajustables según el tipo de club

Esta arquitectura garantiza que el sistema pueda adaptarse a las necesidades específicas de cualquier tipo de club, manteniendo la coherencia y escalabilidad del código.

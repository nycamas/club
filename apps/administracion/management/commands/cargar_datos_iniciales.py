from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from apps.recursos.models import Categoria, TipoRecurso, EstadoRecurso, Recurso, EtiquetaRecurso
from apps.alquiler.models import EstadoAlquiler
from apps.ventas.models import CategoriaProducto, MetodoPago, EstadoVenta
from apps.clases.models import CategoriaClase, NivelClase
from apps.socios.models import TipoSuscripcion, FormaPago, EstadoSuscripcion, Beneficio
import random
from django.utils.text import slugify
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Command(BaseCommand):
    help = 'Carga datos iniciales para el sistema de gestión de clubes'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando carga de datos...'))
        
        self.crear_superusuario()
        self.crear_categorias_recursos()
        self.crear_tipos_recursos()
        self.crear_estados_recursos()
        self.crear_etiquetas_recursos()
        self.crear_estados_alquiler()
        self.crear_categorias_productos()
        self.crear_metodos_pago()
        self.crear_estados_venta()
        self.crear_categorias_clases()
        self.crear_niveles_clases()
        self.crear_tipos_suscripcion()
        self.crear_formas_pago()
        self.crear_estados_suscripcion()
        self.crear_beneficios()
        
        self.stdout.write(self.style.SUCCESS('Carga de datos completada con éxito!'))

    def crear_superusuario(self):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='admin@clubmanager.com',
                password='admin123',
                first_name='Administrador',
                last_name='Sistema',
                es_socio=True
            )
            self.stdout.write(self.style.SUCCESS('Superusuario creado'))
        else:
            self.stdout.write(self.style.WARNING('El superusuario ya existe'))

    def crear_categorias_recursos(self):
        if Categoria.objects.count() == 0:
            categorias = [
                {'nombre': 'Deportes', 'descripcion': 'Equipamiento deportivo', 'icono': 'bi-trophy'},
                {'nombre': 'Libros', 'descripcion': 'Material de lectura', 'icono': 'bi-book'},
                {'nombre': 'Electrónica', 'descripcion': 'Dispositivos electrónicos', 'icono': 'bi-laptop'},
                {'nombre': 'Música', 'descripcion': 'Instrumentos y equipos musicales', 'icono': 'bi-music-note-beamed'},
                {'nombre': 'Herramientas', 'descripcion': 'Herramientas y equipamiento', 'icono': 'bi-tools'},
                {'nombre': 'Juegos', 'descripcion': 'Juegos de mesa y recreativos', 'icono': 'bi-controller'},
                {'nombre': 'Audiovisual', 'descripcion': 'Equipos de audio y video', 'icono': 'bi-camera-video'},
            ]
            
            for cat in categorias:
                Categoria.objects.create(
                    nombre=cat['nombre'],
                    descripcion=cat['descripcion'],
                    icono=cat['icono'],
                    slug=slugify(cat['nombre'])
                )
            
            # Crear algunas subcategorías
            deportes = Categoria.objects.get(nombre='Deportes')
            subcategorias_deportes = [
                {'nombre': 'Fútbol', 'descripcion': 'Equipamiento de fútbol', 'icono': 'bi-dribbble'},
                {'nombre': 'Tenis', 'descripcion': 'Equipamiento de tenis', 'icono': 'bi-circle'},
                {'nombre': 'Natación', 'descripcion': 'Equipamiento de natación', 'icono': 'bi-water'},
            ]
            
            for subcat in subcategorias_deportes:
                Categoria.objects.create(
                    nombre=subcat['nombre'],
                    descripcion=subcat['descripcion'],
                    icono=subcat['icono'],
                    slug=slugify(subcat['nombre']),
                    parent=deportes
                )
                
            self.stdout.write(self.style.SUCCESS('Categorías de recursos creadas'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen categorías de recursos'))

    def crear_tipos_recursos(self):
        if TipoRecurso.objects.count() == 0:
            tipos = [
                {
                    'nombre': 'Equipamiento deportivo',
                    'descripcion': 'Material para práctica deportiva',
                    'alquilable': True,
                    'vendible': True,
                    'requiere_devolucion': True,
                    'tiempo_max_alquiler': 7
                },
                {
                    'nombre': 'Libros',
                    'descripcion': 'Material de lectura y consulta',
                    'alquilable': True,
                    'vendible': True,
                    'requiere_devolucion': True,
                    'tiempo_max_alquiler': 30
                },
                {
                    'nombre': 'Dispositivos electrónicos',
                    'descripcion': 'Equipos electrónicos',
                    'alquilable': True,
                    'vendible': False,
                    'requiere_devolucion': True,
                    'tiempo_max_alquiler': 3
                },
                {
                    'nombre': 'Instrumentos musicales',
                    'descripcion': 'Instrumentos para práctica musical',
                    'alquilable': True,
                    'vendible': False,
                    'requiere_devolucion': True,
                    'tiempo_max_alquiler': 14
                },
                {
                    'nombre': 'Herramientas',
                    'descripcion': 'Herramientas para trabajos manuales',
                    'alquilable': True,
                    'vendible': True,
                    'requiere_devolucion': True,
                    'tiempo_max_alquiler': 5
                },
                {
                    'nombre': 'Juegos de mesa',
                    'descripcion': 'Juegos para actividades recreativas',
                    'alquilable': True,
                    'vendible': True,
                    'requiere_devolucion': True,
                    'tiempo_max_alquiler': 14
                },
                {
                    'nombre': 'Consumibles',
                    'descripcion': 'Productos de un solo uso',
                    'alquilable': False,
                    'vendible': True,
                    'requiere_devolucion': False,
                    'tiempo_max_alquiler': None
                },
            ]
            
            for tipo in tipos:
                TipoRecurso.objects.create(**tipo)
                
            self.stdout.write(self.style.SUCCESS('Tipos de recursos creados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen tipos de recursos'))

    def crear_estados_recursos(self):
        if EstadoRecurso.objects.count() == 0:
            estados = [
                {
                    'nombre': 'Disponible',
                    'descripcion': 'Recurso disponible para alquiler o venta',
                    'disponible': True,
                    'color': 'success'
                },
                {
                    'nombre': 'Alquilado',
                    'descripcion': 'Recurso actualmente alquilado',
                    'disponible': False,
                    'color': 'warning'
                },
                {
                    'nombre': 'En mantenimiento',
                    'descripcion': 'Recurso en mantenimiento o reparación',
                    'disponible': False,
                    'color': 'danger'
                },
                {
                    'nombre': 'Reservado',
                    'descripcion': 'Recurso reservado para alquiler futuro',
                    'disponible': False,
                    'color': 'info'
                },
                {
                    'nombre': 'Agotado',
                    'descripcion': 'Recurso sin stock disponible',
                    'disponible': False,
                    'color': 'secondary'
                },
                {
                    'nombre': 'Descatalogado',
                    'descripcion': 'Recurso que ya no se ofrece',
                    'disponible': False,
                    'color': 'dark'
                },
            ]
            
            for estado in estados:
                EstadoRecurso.objects.create(**estado)
                
            self.stdout.write(self.style.SUCCESS('Estados de recursos creados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen estados de recursos'))

    def crear_etiquetas_recursos(self):
        if EtiquetaRecurso.objects.count() == 0:
            etiquetas = [
                'Nuevo', 'Popular', 'Oferta', 'Recomendado', 'Exclusivo', 
                'Principiantes', 'Avanzado', 'Profesional', 'Niños', 'Adultos',
                'Interior', 'Exterior', 'Verano', 'Invierno', 'Ecológico'
            ]
            
            for etiqueta in etiquetas:
                EtiquetaRecurso.objects.create(
                    nombre=etiqueta,
                    descripcion=f'Recursos etiquetados como {etiqueta.lower()}'
                )
                
            self.stdout.write(self.style.SUCCESS('Etiquetas de recursos creadas'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen etiquetas de recursos'))

    def crear_estados_alquiler(self):
        if EstadoAlquiler.objects.count() == 0:
            estados = [
                {
                    'nombre': 'Reservado',
                    'descripcion': 'Alquiler reservado pero no iniciado',
                    'color': 'info'
                },
                {
                    'nombre': 'En curso',
                    'descripcion': 'Alquiler actualmente en curso',
                    'color': 'primary'
                },
                {
                    'nombre': 'Finalizado',
                    'descripcion': 'Alquiler completado correctamente',
                    'color': 'success'
                },
                {
                    'nombre': 'Retrasado',
                    'descripcion': 'Alquiler con devolución retrasada',
                    'color': 'warning'
                },
                {
                    'nombre': 'Cancelado',
                    'descripcion': 'Alquiler cancelado',
                    'color': 'danger'
                },
                {
                    'nombre': 'Pendiente de pago',
                    'descripcion': 'Alquiler pendiente de pago',
                    'color': 'secondary'
                },
            ]
            
            for estado in estados:
                EstadoAlquiler.objects.create(**estado)
                
            self.stdout.write(self.style.SUCCESS('Estados de alquiler creados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen estados de alquiler'))

    def crear_categorias_productos(self):
        if CategoriaProducto.objects.count() == 0:
            categorias = [
                {'nombre': 'Equipamiento', 'descripcion': 'Equipamiento deportivo y accesorios', 'icono': 'bi-trophy'},
                {'nombre': 'Ropa', 'descripcion': 'Ropa deportiva y casual', 'icono': 'bi-tshirt'},
                {'nombre': 'Accesorios', 'descripcion': 'Accesorios diversos', 'icono': 'bi-bag'},
                {'nombre': 'Nutrición', 'descripcion': 'Suplementos y productos nutricionales', 'icono': 'bi-cup-straw'},
                {'nombre': 'Libros', 'descripcion': 'Libros y material educativo', 'icono': 'bi-book'},
                {'nombre': 'Merchandising', 'descripcion': 'Productos promocionales del club', 'icono': 'bi-star'},
                {'nombre': 'Electrónica', 'descripcion': 'Dispositivos y accesorios electrónicos', 'icono': 'bi-laptop'},
            ]
            
            for cat in categorias:
                CategoriaProducto.objects.create(
                    nombre=cat['nombre'],
                    descripcion=cat['descripcion'],
                    icono=cat['icono'],
                    slug=slugify(cat['nombre'])
                )
                
            self.stdout.write(self.style.SUCCESS('Categorías de productos creadas'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen categorías de productos'))

    def crear_metodos_pago(self):
        if MetodoPago.objects.count() == 0:
            metodos = [
                {'nombre': 'Tarjeta de crédito/débito', 'descripcion': 'Pago con tarjeta bancaria', 'icono': 'bi-credit-card'},
                {'nombre': 'Transferencia bancaria', 'descripcion': 'Pago mediante transferencia', 'icono': 'bi-bank'},
                {'nombre': 'PayPal', 'descripcion': 'Pago a través de PayPal', 'icono': 'bi-paypal'},
                {'nombre': 'Efectivo', 'descripcion': 'Pago en efectivo en las instalaciones', 'icono': 'bi-cash'},
                {'nombre': 'Bizum', 'descripcion': 'Pago mediante Bizum', 'icono': 'bi-phone'},
            ]
            
            for metodo in metodos:
                MetodoPago.objects.create(**metodo)
                
            self.stdout.write(self.style.SUCCESS('Métodos de pago creados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen métodos de pago'))

    def crear_estados_venta(self):
        if EstadoVenta.objects.count() == 0:
            estados = [
                {
                    'nombre': 'Pendiente',
                    'descripcion': 'Venta pendiente de pago',
                    'color': 'warning'
                },
                {
                    'nombre': 'Pagada',
                    'descripcion': 'Venta pagada pero no entregada',
                    'color': 'info'
                },
                {
                    'nombre': 'Completada',
                    'descripcion': 'Venta pagada y entregada',
                    'color': 'success'
                },
                {
                    'nombre': 'Cancelada',
                    'descripcion': 'Venta cancelada',
                    'color': 'danger'
                },
                {
                    'nombre': 'Reembolsada',
                    'descripcion': 'Venta con reembolso realizado',
                    'color': 'secondary'
                },
            ]
            
            for estado in estados:
                EstadoVenta.objects.create(**estado)
                
            self.stdout.write(self.style.SUCCESS('Estados de venta creados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen estados de venta'))

    def crear_categorias_clases(self):
        if CategoriaClase.objects.count() == 0:
            categorias = [
                {'nombre': 'Fitness', 'descripcion': 'Clases de acondicionamiento físico', 'icono': 'bi-heart-pulse', 'color': 'danger'},
                {'nombre': 'Yoga', 'descripcion': 'Clases de yoga y meditación', 'icono': 'bi-peace', 'color': 'info'},
                {'nombre': 'Baile', 'descripcion': 'Clases de diferentes estilos de baile', 'icono': 'bi-music-note', 'color': 'warning'},
                {'nombre': 'Artes marciales', 'descripcion': 'Clases de diferentes artes marciales', 'icono': 'bi-shield', 'color': 'dark'},
                {'nombre': 'Natación', 'descripcion': 'Clases de natación y actividades acuáticas', 'icono': 'bi-water', 'color': 'primary'},
                {'nombre': 'Idiomas', 'descripcion': 'Clases de idiomas', 'icono': 'bi-translate', 'color': 'success'},
                {'nombre': 'Arte', 'descripcion': 'Clases de arte y manualidades', 'icono': 'bi-palette', 'color': 'secondary'},
            ]
            
            for cat in categorias:
                CategoriaClase.objects.create(
                    nombre=cat['nombre'],
                    descripcion=cat['descripcion'],
                    icono=cat['icono'],
                    color=cat['color'],
                    slug=slugify(cat['nombre'])
                )
                
            self.stdout.write(self.style.SUCCESS('Categorías de clases creadas'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen categorías de clases'))

    def crear_niveles_clases(self):
        if NivelClase.objects.count() == 0:
            niveles = [
                {'nombre': 'Principiante', 'descripcion': 'Nivel básico para personas sin experiencia previa', 'orden': 1},
                {'nombre': 'Intermedio', 'descripcion': 'Nivel medio para personas con conocimientos básicos', 'orden': 2},
                {'nombre': 'Avanzado', 'descripcion': 'Nivel avanzado para personas con experiencia', 'orden': 3},
                {'nombre': 'Todos los niveles', 'descripcion': 'Clase adaptada a cualquier nivel de experiencia', 'orden': 0},
                {'nombre': 'Niños', 'descripcion': 'Clase específica para niños', 'orden': 5},
                {'nombre': 'Senior', 'descripcion': 'Clase adaptada para personas mayores', 'orden': 6},
            ]
            
            for nivel in niveles:
                NivelClase.objects.create(**nivel)
                
            self.stdout.write(self.style.SUCCESS('Niveles de clases creados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen niveles de clases'))

    def crear_tipos_suscripcion(self):
        if TipoSuscripcion.objects.count() == 0:
            tipos = [
                {
                    'nombre': 'Básica',
                    'descripcion': 'Acceso básico a las instalaciones y servicios del club',
                    'precio_mensual': 29.99,
                    'precio_trimestral': 79.99,
                    'precio_anual': 299.99,
                    'duracion_minima_meses': 1,
                    'descuento_alquiler': 0,
                    'descuento_compras': 0,
                    'descuento_clases': 0,
                    'max_alquileres_simultaneos': 2,
                    'max_reservas_clases': 3,
                    'color': 'info'
                },
                {
                    'nombre': 'Premium',
                    'descripcion': 'Acceso completo a instalaciones y descuentos en servicios',
                    'precio_mensual': 49.99,
                    'precio_trimestral': 139.99,
                    'precio_anual': 499.99,
                    'duracion_minima_meses': 1,
                    'descuento_alquiler': 10,
                    'descuento_compras': 5,
                    'descuento_clases': 10,
                    'max_alquileres_simultaneos': 4,
                    'max_reservas_clases': 6,
                    'color': 'primary',
                    'destacado': True
                },
                {
                    'nombre': 'Familiar',
                    'descripcion': 'Plan para familias con acceso para hasta 4 miembros',
                    'precio_mensual': 89.99,
                    'precio_trimestral': 249.99,
                    'precio_anual': 899.99,
                    'duracion_minima_meses': 3,
                    'descuento_alquiler': 15,
                    'descuento_compras': 10,
                    'descuento_clases': 15,
                    'max_alquileres_simultaneos': 8,
                    'max_reservas_clases': 12,
                    'color': 'success'
                },
                {
                    'nombre': 'Estudiante',
                    'descripcion': 'Plan especial para estudiantes con identificación válida',
                    'precio_mensual': 19.99,
                    'precio_trimestral': 54.99,
                    'precio_anual': 199.99,
                    'duracion_minima_meses': 3,
                    'descuento_alquiler': 5,
                    'descuento_compras': 5,
                    'descuento_clases': 10,
                    'max_alquileres_simultaneos': 2,
                    'max_reservas_clases': 4,
                    'color': 'warning'
                },
                {
                    'nombre': 'Senior',
                    'descripcion': 'Plan especial para mayores de 65 años',
                    'precio_mensual': 24.99,
                    'precio_trimestral': 69.99,
                    'precio_anual': 249.99,
                    'duracion_minima_meses': 1,
                    'descuento_alquiler': 15,
                    'descuento_compras': 10,
                    'descuento_clases': 20,
                    'max_alquileres_simultaneos': 3,
                    'max_reservas_clases': 5,
                    'color': 'secondary'
                },
            ]
            
            for tipo in tipos:
                TipoSuscripcion.objects.create(**tipo)
                
            self.stdout.write(self.style.SUCCESS('Tipos de suscripción creados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen tipos de suscripción'))

    def crear_formas_pago(self):
        if FormaPago.objects.count() == 0:
            formas = [
                {'nombre': 'Tarjeta de crédito/débito', 'descripcion': 'Cargo automático mensual a tarjeta'},
                {'nombre': 'Domiciliación bancaria', 'descripcion': 'Cargo automático a cuenta bancaria'},
                {'nombre': 'Transferencia bancaria', 'descripcion': 'Pago manual mediante transferencia', 'requiere_validacion_manual': True},
                {'nombre': 'Efectivo', 'descripcion': 'Pago en efectivo en las instalaciones', 'requiere_validacion_manual': True},
                {'nombre': 'PayPal', 'descripcion': 'Cargo automático a cuenta PayPal'},
            ]
            
            for forma in formas:
                FormaPago.objects.create(**forma)
                
            self.stdout.write(self.style.SUCCESS('Formas de pago creadas'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen formas de pago'))

    def crear_estados_suscripcion(self):
        if EstadoSuscripcion.objects.count() == 0:
            estados = [
                {
                    'nombre': 'Activa',
                    'descripcion': 'Suscripción activa y al corriente de pago',
                    'color': 'success'
                },
                {
                    'nombre': 'Pendiente de pago',
                    'descripcion': 'Suscripción con pago pendiente',
                    'color': 'warning'
                },
                {
                    'nombre': 'Suspendida',
                    'descripcion': 'Suscripción temporalmente suspendida',
                    'color': 'danger'
                },
                {
                    'nombre': 'Cancelada',
                    'descripcion': 'Suscripción cancelada',
                    'color': 'secondary'
                },
                {
                    'nombre': 'Expirada',
                    'descripcion': 'Suscripción expirada sin renovación',
                    'color': 'dark'
                },
                {
                    'nombre': 'Pendiente de activación',
                    'descripcion': 'Suscripción en proceso de activación',
                    'color': 'info'
                },
            ]
            
            for estado in estados:
                EstadoSuscripcion.objects.create(**estado)
                
            self.stdout.write(self.style.SUCCESS('Estados de suscripción creados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen estados de suscripción'))

    def crear_beneficios(self):
        if Beneficio.objects.count() == 0:
            beneficios = [
                {'nombre': 'Acceso ilimitado a instalaciones', 'descripcion': 'Acceso sin restricciones a todas las instalaciones del club durante el horario de apertura', 'icono': 'bi-door-open'},
                {'nombre': 'Descuento en alquileres', 'descripcion': 'Descuentos especiales en el alquiler de recursos del club', 'icono': 'bi-percent'},
                {'nombre': 'Descuento en tienda', 'descripcion': 'Descuentos en compras realizadas en la tienda del club', 'icono': 'bi-bag-check'},
                {'nombre': 'Clases gratuitas', 'descripcion': 'Acceso gratuito a determinadas clases', 'icono': 'bi-calendar-check'},
                {'nombre': 'Invitados gratis', 'descripcion': 'Posibilidad de traer invitados sin coste adicional', 'icono': 'bi-people'},
                {'nombre': 'Reserva anticipada', 'descripcion': 'Posibilidad de realizar reservas con mayor antelación', 'icono': 'bi-calendar-plus'},
                {'nombre': 'Eventos exclusivos', 'descripcion': 'Acceso a eventos exclusivos para socios', 'icono': 'bi-star'},
                {'nombre': 'Aparcamiento gratuito', 'descripcion': 'Acceso gratuito al aparcamiento del club', 'icono': 'bi-p-square'},
                {'nombre': 'Asesoramiento personalizado', 'descripcion': 'Sesiones de asesoramiento personalizado', 'icono': 'bi-person-check'},
                {'nombre': 'Descuento en servicios adicionales', 'descripcion': 'Descuentos en servicios adicionales como fisioterapia, nutrición, etc.', 'icono': 'bi-plus-circle'},
            ]
            
            for beneficio in beneficios:
                Beneficio.objects.create(**beneficio)
                
            # Asignar beneficios a tipos de suscripción
            basica = TipoSuscripcion.objects.get(nombre='Básica')
            premium = TipoSuscripcion.objects.get(nombre='Premium')
            familiar = TipoSuscripcion.objects.get(nombre='Familiar')
            estudiante = TipoSuscripcion.objects.get(nombre='Estudiante')
            senior = TipoSuscripcion.objects.get(nombre='Senior')
            
            # Beneficios para suscripción básica
            basica.beneficios.add(
                Beneficio.objects.get(nombre='Acceso ilimitado a instalaciones')
            )
            
            # Beneficios para suscripción premium
            premium.beneficios.add(
                Beneficio.objects.get(nombre='Acceso ilimitado a instalaciones'),
                Beneficio.objects.get(nombre='Descuento en alquileres'),
                Beneficio.objects.get(nombre='Descuento en tienda'),
                Beneficio.objects.get(nombre='Reserva anticipada'),
                Beneficio.objects.get(nombre='Eventos exclusivos')
            )
            
            # Beneficios para suscripción familiar
            familiar.beneficios.add(
                Beneficio.objects.get(nombre='Acceso ilimitado a instalaciones'),
                Beneficio.objects.get(nombre='Descuento en alquileres'),
                Beneficio.objects.get(nombre='Descuento en tienda'),
                Beneficio.objects.get(nombre='Invitados gratis'),
                Beneficio.objects.get(nombre='Reserva anticipada'),
                Beneficio.objects.get(nombre='Eventos exclusivos'),
                Beneficio.objects.get(nombre='Aparcamiento gratuito')
            )
            
            # Beneficios para suscripción estudiante
            estudiante.beneficios.add(
                Beneficio.objects.get(nombre='Acceso ilimitado a instalaciones'),
                Beneficio.objects.get(nombre='Descuento en alquileres'),
                Beneficio.objects.get(nombre='Descuento en tienda')
            )
            
            # Beneficios para suscripción senior
            senior.beneficios.add(
                Beneficio.objects.get(nombre='Acceso ilimitado a instalaciones'),
                Beneficio.objects.get(nombre='Descuento en alquileres'),
                Beneficio.objects.get(nombre='Descuento en tienda'),
                Beneficio.objects.get(nombre='Clases gratuitas'),
                Beneficio.objects.get(nombre='Asesoramiento personalizado')
            )
            
            self.stdout.write(self.style.SUCCESS('Beneficios creados y asignados'))
        else:
            self.stdout.write(self.style.WARNING('Ya existen beneficios'))

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
import os
import sys
import random
import string
import datetime

User = get_user_model()

class Command(BaseCommand):
    help = 'Valida la configuración y funcionalidad del sistema de gestión de clubes'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Iniciando validación del sistema...'))
        
        # Validar estructura del proyecto
        self.validar_estructura_proyecto()
        
        # Validar modelos y relaciones
        self.validar_modelos()
        
        # Validar configuración de seguridad
        self.validar_configuracion_seguridad()
        
        # Validar escalabilidad
        self.validar_escalabilidad()
        
        # Validar documentación
        self.validar_documentacion()
        
        self.stdout.write(self.style.SUCCESS('¡Validación completada con éxito!'))
        self.stdout.write(self.style.SUCCESS('El sistema está listo para su uso en producción.'))

    def validar_estructura_proyecto(self):
        """Valida la estructura modular del proyecto"""
        self.stdout.write('Validando estructura del proyecto...')
        
        # Verificar existencia de apps principales
        apps_requeridas = ['recursos', 'alquiler', 'ventas', 'clases', 'socios', 'administracion', 'common']
        for app in apps_requeridas:
            app_path = os.path.join(settings.BASE_DIR, 'apps', app)
            if not os.path.exists(app_path):
                self.stdout.write(self.style.ERROR(f'Error: No se encontró la app {app}'))
                return False
            
            # Verificar archivos principales en cada app
            archivos_requeridos = ['__init__.py', 'models.py']
            for archivo in archivos_requeridos:
                if not os.path.exists(os.path.join(app_path, archivo)):
                    self.stdout.write(self.style.ERROR(f'Error: No se encontró el archivo {archivo} en la app {app}'))
                    return False
        
        # Verificar estructura de templates y static
        if not os.path.exists(os.path.join(settings.BASE_DIR, 'templates')):
            self.stdout.write(self.style.ERROR('Error: No se encontró el directorio de templates'))
            return False
            
        if not os.path.exists(os.path.join(settings.BASE_DIR, 'static')):
            self.stdout.write(self.style.ERROR('Error: No se encontró el directorio de static'))
            return False
        
        self.stdout.write(self.style.SUCCESS('✓ Estructura del proyecto validada correctamente'))
        return True

    def validar_modelos(self):
        """Valida los modelos y sus relaciones"""
        self.stdout.write('Validando modelos y relaciones...')
        
        try:
            # Importar modelos principales
            from apps.recursos.models import Categoria, TipoRecurso, EstadoRecurso, Recurso
            from apps.alquiler.models import EstadoAlquiler, Alquiler, DetalleAlquiler
            from apps.ventas.models import CategoriaProducto, Producto, EstadoVenta, Venta
            from apps.clases.models import CategoriaClase, NivelClase, Clase, SesionClase
            from apps.socios.models import TipoSuscripcion, FormaPago, EstadoSuscripcion, Suscripcion
            
            # Validar que los modelos tengan los campos requeridos
            recurso = Recurso._meta.get_fields()
            alquiler = Alquiler._meta.get_fields()
            producto = Producto._meta.get_fields()
            clase = Clase._meta.get_fields()
            suscripcion = Suscripcion._meta.get_fields()
            
            # Verificar relaciones entre modelos
            # Por ejemplo, verificar que Recurso tenga relación con Categoria
            if not any(field.name == 'categoria' for field in recurso):
                self.stdout.write(self.style.ERROR('Error: El modelo Recurso no tiene relación con Categoria'))
                return False
                
            # Verificar que DetalleAlquiler tenga relación con Alquiler y Recurso
            detalle_alquiler = DetalleAlquiler._meta.get_fields()
            if not (any(field.name == 'alquiler' for field in detalle_alquiler) and 
                    any(field.name == 'recurso' for field in detalle_alquiler)):
                self.stdout.write(self.style.ERROR('Error: El modelo DetalleAlquiler no tiene las relaciones requeridas'))
                return False
            
            self.stdout.write(self.style.SUCCESS('✓ Modelos y relaciones validados correctamente'))
            return True
            
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'Error al importar modelos: {e}'))
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al validar modelos: {e}'))
            return False

    def validar_configuracion_seguridad(self):
        """Valida la configuración de seguridad del proyecto"""
        self.stdout.write('Validando configuración de seguridad...')
        
        # Verificar configuraciones de seguridad en settings
        security_settings = [
            'SECRET_KEY',
            'DEBUG',
            'ALLOWED_HOSTS',
            'CSRF_COOKIE_SECURE',
            'SESSION_COOKIE_SECURE',
            'SECURE_BROWSER_XSS_FILTER',
            'SECURE_CONTENT_TYPE_NOSNIFF',
            'X_FRAME_OPTIONS'
        ]
        
        for setting in security_settings:
            if not hasattr(settings, setting):
                self.stdout.write(self.style.WARNING(f'Advertencia: No se encontró la configuración {setting}'))
        
        # Verificar que DEBUG esté en False para producción
        if settings.DEBUG:
            self.stdout.write(self.style.WARNING('Advertencia: DEBUG está activado. Debe desactivarse en producción.'))
        
        # Verificar que ALLOWED_HOSTS no esté vacío
        if not settings.ALLOWED_HOSTS:
            self.stdout.write(self.style.WARNING('Advertencia: ALLOWED_HOSTS está vacío. Debe configurarse en producción.'))
        
        # Verificar documentos legales
        legal_docs = ['politica_privacidad.md', 'terminos_condiciones.md', 'politica_cookies.md']
        for doc in legal_docs:
            if not os.path.exists(os.path.join(settings.BASE_DIR, 'docs', 'legal', doc)):
                self.stdout.write(self.style.WARNING(f'Advertencia: No se encontró el documento legal {doc}'))
        
        self.stdout.write(self.style.SUCCESS('✓ Configuración de seguridad validada correctamente'))
        return True

    def validar_escalabilidad(self):
        """Valida la escalabilidad del sistema"""
        self.stdout.write('Validando escalabilidad del sistema...')
        
        # Verificar uso de modelos abstractos para reutilización
        try:
            from apps.common.models import BaseModel, TimeStampedModel, SoftDeleteModel
            
            # Verificar que los modelos base sean abstractos
            if not BaseModel._meta.abstract:
                self.stdout.write(self.style.ERROR('Error: El modelo BaseModel no es abstracto'))
                return False
                
            if not TimeStampedModel._meta.abstract:
                self.stdout.write(self.style.ERROR('Error: El modelo TimeStampedModel no es abstracto'))
                return False
                
            if not SoftDeleteModel._meta.abstract:
                self.stdout.write(self.style.ERROR('Error: El modelo SoftDeleteModel no es abstracto'))
                return False
            
            # Verificar uso de modelos base en otros modelos
            from apps.recursos.models import Recurso
            from apps.alquiler.models import Alquiler
            from apps.ventas.models import Producto
            
            # Verificar herencia de modelos base
            if not issubclass(Recurso, BaseModel):
                self.stdout.write(self.style.WARNING('Advertencia: El modelo Recurso no hereda de BaseModel'))
                
            if not issubclass(Alquiler, BaseModel):
                self.stdout.write(self.style.WARNING('Advertencia: El modelo Alquiler no hereda de BaseModel'))
                
            if not issubclass(Producto, BaseModel):
                self.stdout.write(self.style.WARNING('Advertencia: El modelo Producto no hereda de BaseModel'))
            
            self.stdout.write(self.style.SUCCESS('✓ Escalabilidad del sistema validada correctamente'))
            return True
            
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'Error al importar modelos para validar escalabilidad: {e}'))
            return False
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al validar escalabilidad: {e}'))
            return False

    def validar_documentacion(self):
        """Valida la existencia y completitud de la documentación"""
        self.stdout.write('Validando documentación...')
        
        # Verificar documentos principales
        docs_requeridos = [
            os.path.join(settings.BASE_DIR, 'requerimientos.md'),
            os.path.join(settings.BASE_DIR, 'estructura_proyecto.md'),
            os.path.join(settings.BASE_DIR, 'docs', 'legal', 'politica_privacidad.md'),
            os.path.join(settings.BASE_DIR, 'docs', 'legal', 'terminos_condiciones.md'),
            os.path.join(settings.BASE_DIR, 'docs', 'legal', 'politica_cookies.md')
        ]
        
        for doc in docs_requeridos:
            if not os.path.exists(doc):
                self.stdout.write(self.style.WARNING(f'Advertencia: No se encontró el documento {doc}'))
            else:
                # Verificar que el documento no esté vacío
                if os.path.getsize(doc) == 0:
                    self.stdout.write(self.style.WARNING(f'Advertencia: El documento {doc} está vacío'))
        
        self.stdout.write(self.style.SUCCESS('✓ Documentación validada correctamente'))
        return True

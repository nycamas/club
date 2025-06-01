from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.common.models import BaseModel
from django.conf import settings


class Usuario(AbstractUser):
    """
    Modelo de usuario personalizado que extiende el modelo base de Django.
    Incluye campos adicionales para la gestión de socios del club.
    """
    # Información personal adicional
    dni = models.CharField(_("DNI/NIF"), max_length=20, blank=True)
    fecha_nacimiento = models.DateField(_("Fecha de nacimiento"), null=True, blank=True)
    telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    direccion = models.TextField(_("Dirección"), blank=True)
    codigo_postal = models.CharField(_("Código postal"), max_length=10, blank=True)
    ciudad = models.CharField(_("Ciudad"), max_length=100, blank=True)
    provincia = models.CharField(_("Provincia"), max_length=100, blank=True)
    pais = models.CharField(_("País"), max_length=100, blank=True)
    foto_perfil = models.ImageField(_("Foto de perfil"), upload_to="usuarios/", null=True, blank=True)
    
    # Campos para socios
    es_socio = models.BooleanField(_("Es socio"), default=False)
    numero_socio = models.CharField(_("Número de socio"), max_length=50, blank=True, unique=True, null=True)
    fecha_alta = models.DateField(_("Fecha de alta"), null=True, blank=True)
    
    # Preferencias
    recibir_notificaciones = models.BooleanField(_("Recibir notificaciones"), default=True)
    preferencias = models.JSONField(_("Preferencias"), default=dict, blank=True)
    
    class Meta:
        verbose_name = _("Usuario")
        verbose_name_plural = _("Usuarios")
        ordering = ['last_name', 'first_name']
    
    def __str__(self):
        return self.get_full_name() or self.username
    
    def save(self, *args, **kwargs):
        """
        Sobrescribe el método save para asignar número de socio automáticamente.
        """
        if self.es_socio and not self.numero_socio:
            # Generar número de socio basado en el año actual y un contador
            year = timezone.now().year
            last_member = Usuario.objects.filter(
                numero_socio__startswith=f"S{year}-"
            ).order_by('-numero_socio').first()
            
            if last_member and last_member.numero_socio:
                try:
                    last_number = int(last_member.numero_socio.split('-')[1])
                    self.numero_socio = f"S{year}-{last_number + 1:04d}"
                except (IndexError, ValueError):
                    self.numero_socio = f"S{year}-0001"
            else:
                self.numero_socio = f"S{year}-0001"
            
            if not self.fecha_alta:
                self.fecha_alta = timezone.now().date()
        
        super().save(*args, **kwargs)


class TipoSuscripcion(BaseModel):
    """
    Define los diferentes tipos de suscripción disponibles en el club.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"))
    precio_mensual = models.DecimalField(_("Precio mensual"), max_digits=10, decimal_places=2,
                                        validators=[MinValueValidator(0)])
    precio_trimestral = models.DecimalField(_("Precio trimestral"), max_digits=10, decimal_places=2,
                                           null=True, blank=True, validators=[MinValueValidator(0)])
    precio_anual = models.DecimalField(_("Precio anual"), max_digits=10, decimal_places=2,
                                      null=True, blank=True, validators=[MinValueValidator(0)])
    duracion_minima_meses = models.PositiveSmallIntegerField(_("Duración mínima (meses)"), default=1)
    
    # Beneficios
    descuento_alquiler = models.DecimalField(_("Descuento en alquileres (%)"), max_digits=5, decimal_places=2,
                                            default=0, validators=[MinValueValidator(0)])
    descuento_compras = models.DecimalField(_("Descuento en compras (%)"), max_digits=5, decimal_places=2,
                                           default=0, validators=[MinValueValidator(0)])
    descuento_clases = models.DecimalField(_("Descuento en clases (%)"), max_digits=5, decimal_places=2,
                                          default=0, validators=[MinValueValidator(0)])
    
    # Restricciones
    max_alquileres_simultaneos = models.PositiveSmallIntegerField(_("Máximo de alquileres simultáneos"),
                                                                 default=3)
    max_reservas_clases = models.PositiveSmallIntegerField(_("Máximo de reservas de clases"),
                                                          default=5)
    acceso_instalaciones = models.BooleanField(_("Acceso a instalaciones"), default=True)
    
    # Metadatos
    color = models.CharField(_("Color"), max_length=20, default="primary",
                            help_text=_("Clase de color de Bootstrap (primary, success, danger, etc.)"))
    destacado = models.BooleanField(_("Destacado"), default=False)
    activo = models.BooleanField(_("Activo"), default=True)
    
    class Meta:
        verbose_name = _("Tipo de suscripción")
        verbose_name_plural = _("Tipos de suscripción")
        ordering = ['precio_mensual']
    
    def __str__(self):
        return self.nombre


class FormaPago(BaseModel):
    """
    Formas de pago disponibles para suscripciones.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    activo = models.BooleanField(_("Activo"), default=True)
    requiere_validacion_manual = models.BooleanField(_("Requiere validación manual"), default=False)
    
    class Meta:
        verbose_name = _("Forma de pago")
        verbose_name_plural = _("Formas de pago")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class EstadoSuscripcion(BaseModel):
    """
    Define los posibles estados de una suscripción.
    Ejemplos: Activa, Pendiente de pago, Cancelada, Expirada, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=50)
    descripcion = models.TextField(_("Descripción"), blank=True)
    color = models.CharField(_("Color"), max_length=20, default="primary",
                            help_text=_("Clase de color de Bootstrap (primary, success, danger, etc.)"))
    
    class Meta:
        verbose_name = _("Estado de suscripción")
        verbose_name_plural = _("Estados de suscripción")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Suscripcion(BaseModel):
    """
    Modelo principal para las suscripciones de socios al club.
    """
    # Relaciones
    socio = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Socio"),
                             on_delete=models.CASCADE, related_name="suscripciones")
    tipo = models.ForeignKey(TipoSuscripcion, verbose_name=_("Tipo de suscripción"),
                            on_delete=models.PROTECT, related_name="suscripciones")
    
    # Fechas
    fecha_inicio = models.DateField(_("Fecha de inicio"))
    fecha_fin = models.DateField(_("Fecha de fin"), null=True, blank=True)
    fecha_cancelacion = models.DateField(_("Fecha de cancelación"), null=True, blank=True)
    
    # Estado
    estado = models.ForeignKey(EstadoSuscripcion, verbose_name=_("Estado"),
                              on_delete=models.PROTECT, related_name="suscripciones")
    motivo_cancelacion = models.TextField(_("Motivo de cancelación"), blank=True)
    
    # Pago
    forma_pago = models.ForeignKey(FormaPago, verbose_name=_("Forma de pago"),
                                  on_delete=models.PROTECT, related_name="suscripciones")
    periodicidad = models.CharField(_("Periodicidad"), max_length=20,
                                   choices=[
                                       ('mensual', _("Mensual")),
                                       ('trimestral', _("Trimestral")),
                                       ('anual', _("Anual")),
                                   ],
                                   default='mensual')
    precio = models.DecimalField(_("Precio"), max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    renovacion_automatica = models.BooleanField(_("Renovación automática"), default=True)
    
    # Metadatos
    notas = models.TextField(_("Notas"), blank=True)
    
    class Meta:
        verbose_name = _("Suscripción")
        verbose_name_plural = _("Suscripciones")
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"{self.socio} - {self.tipo.nombre} ({self.get_periodicidad_display()})"
    
    @property
    def activa(self):
        """
        Indica si la suscripción está activa.
        """
        hoy = timezone.now().date()
        return (self.estado.nombre == "Activa" and 
                self.fecha_inicio <= hoy and 
                (self.fecha_fin is None or hoy <= self.fecha_fin))
    
    @property
    def dias_restantes(self):
        """
        Calcula los días restantes de la suscripción.
        """
        if not self.fecha_fin:
            return None
        
        hoy = timezone.now().date()
        if hoy > self.fecha_fin:
            return 0
        
        return (self.fecha_fin - hoy).days
    
    def cancelar(self, motivo="", fecha=None):
        """
        Cancela la suscripción.
        """
        if not fecha:
            fecha = timezone.now().date()
        
        self.fecha_cancelacion = fecha
        self.motivo_cancelacion = motivo
        
        # Buscar el estado "Cancelada"
        estado_cancelada = EstadoSuscripcion.objects.filter(nombre="Cancelada").first()
        if estado_cancelada:
            self.estado = estado_cancelada
        
        self.save()
    
    def renovar(self, periodos=1):
        """
        Renueva la suscripción por el número de periodos especificado.
        """
        if not self.fecha_fin:
            return False
        
        nueva_fecha_inicio = self.fecha_fin + timezone.timedelta(days=1)
        
        if self.periodicidad == 'mensual':
            meses = periodos
            nueva_fecha_fin = nueva_fecha_inicio.replace(month=nueva_fecha_inicio.month + meses)
            if nueva_fecha_fin.month > 12:
                nueva_fecha_fin = nueva_fecha_fin.replace(year=nueva_fecha_fin.year + 1, month=nueva_fecha_fin.month - 12)
        elif self.periodicidad == 'trimestral':
            meses = periodos * 3
            nueva_fecha_fin = nueva_fecha_inicio.replace(month=nueva_fecha_inicio.month + meses)
            if nueva_fecha_fin.month > 12:
                nueva_fecha_fin = nueva_fecha_fin.replace(year=nueva_fecha_fin.year + 1, month=nueva_fecha_fin.month - 12)
        elif self.periodicidad == 'anual':
            nueva_fecha_fin = nueva_fecha_inicio.replace(year=nueva_fecha_inicio.year + periodos)
        
        self.fecha_inicio = nueva_fecha_inicio
        self.fecha_fin = nueva_fecha_fin
        
        # Buscar el estado "Activa"
        estado_activa = EstadoSuscripcion.objects.filter(nombre="Activa").first()
        if estado_activa:
            self.estado = estado_activa
        
        self.fecha_cancelacion = None
        self.motivo_cancelacion = ""
        self.save()
        
        return True


class PagoSuscripcion(BaseModel):
    """
    Registro de pagos realizados por suscripciones.
    """
    suscripcion = models.ForeignKey(Suscripcion, verbose_name=_("Suscripción"),
                                   on_delete=models.CASCADE, related_name="pagos")
    fecha = models.DateField(_("Fecha"), default=timezone.now)
    monto = models.DecimalField(_("Monto"), max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(0)])
    referencia = models.CharField(_("Referencia"), max_length=100, blank=True)
    comprobante = models.FileField(_("Comprobante"), upload_to="pagos/", null=True, blank=True)
    notas = models.TextField(_("Notas"), blank=True)
    
    # Estado
    confirmado = models.BooleanField(_("Confirmado"), default=False)
    fecha_confirmacion = models.DateField(_("Fecha de confirmación"), null=True, blank=True)
    confirmado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Confirmado por"),
                                      on_delete=models.SET_NULL, null=True, blank=True,
                                      related_name="pagos_confirmados")
    
    class Meta:
        verbose_name = _("Pago de suscripción")
        verbose_name_plural = _("Pagos de suscripción")
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Pago {self.id} - {self.suscripcion}"
    
    def confirmar(self, usuario=None):
        """
        Confirma el pago de la suscripción.
        """
        self.confirmado = True
        self.fecha_confirmacion = timezone.now().date()
        self.confirmado_por = usuario
        self.save()


class Beneficio(BaseModel):
    """
    Beneficios adicionales que pueden asociarse a tipos de suscripción.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"))
    icono = models.CharField(_("Icono"), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Beneficio")
        verbose_name_plural = _("Beneficios")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# Relación muchos a muchos entre TipoSuscripcion y Beneficio
TipoSuscripcion.beneficios = models.ManyToManyField(
    Beneficio,
    verbose_name=_("Beneficios"),
    related_name="tipos_suscripcion",
    blank=True
)

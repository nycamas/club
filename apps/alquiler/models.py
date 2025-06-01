from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.common.models import BaseModel
from apps.recursos.models import Recurso
from django.conf import settings


class EstadoAlquiler(BaseModel):
    """
    Define los posibles estados de un alquiler.
    Ejemplos: Reservado, En curso, Finalizado, Cancelado, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=50)
    descripcion = models.TextField(_("Descripción"), blank=True)
    color = models.CharField(_("Color"), max_length=20, default="primary",
                            help_text=_("Clase de color de Bootstrap (primary, success, danger, etc.)"))
    
    class Meta:
        verbose_name = _("Estado de alquiler")
        verbose_name_plural = _("Estados de alquiler")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Alquiler(BaseModel):
    """
    Modelo principal para gestionar los alquileres de recursos del club.
    """
    # Identificación y relaciones
    codigo = models.CharField(_("Código"), max_length=50, unique=True)
    socio = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Socio"),
                             on_delete=models.PROTECT, related_name="alquileres")
    
    # Fechas
    fecha_solicitud = models.DateTimeField(_("Fecha de solicitud"), auto_now_add=True)
    fecha_inicio = models.DateField(_("Fecha de inicio"))
    fecha_fin_prevista = models.DateField(_("Fecha de fin prevista"))
    fecha_devolucion = models.DateField(_("Fecha de devolución real"), null=True, blank=True)
    
    # Estado y seguimiento
    estado = models.ForeignKey(EstadoAlquiler, verbose_name=_("Estado"),
                              on_delete=models.PROTECT, related_name="alquileres")
    notas = models.TextField(_("Notas"), blank=True)
    
    # Costos
    costo_total = models.DecimalField(_("Costo total"), max_digits=10, decimal_places=2,
                                     validators=[MinValueValidator(0)])
    deposito = models.DecimalField(_("Depósito"), max_digits=10, decimal_places=2,
                                  default=0, validators=[MinValueValidator(0)])
    deposito_devuelto = models.DecimalField(_("Depósito devuelto"), max_digits=10, decimal_places=2,
                                           null=True, blank=True, validators=[MinValueValidator(0)])
    
    # Gestión
    gestionado_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Gestionado por"),
                                      on_delete=models.PROTECT, related_name="alquileres_gestionados",
                                      null=True, blank=True)
    
    class Meta:
        verbose_name = _("Alquiler")
        verbose_name_plural = _("Alquileres")
        ordering = ['-fecha_solicitud']
    
    def __str__(self):
        return f"Alquiler {self.codigo} - {self.socio.username}"
    
    @property
    def dias_alquiler(self):
        """
        Calcula la duración prevista del alquiler en días.
        """
        return (self.fecha_fin_prevista - self.fecha_inicio).days
    
    @property
    def esta_en_curso(self):
        """
        Indica si el alquiler está actualmente en curso.
        """
        hoy = timezone.now().date()
        return (self.fecha_inicio <= hoy and 
                (self.fecha_devolucion is None or hoy <= self.fecha_devolucion))
    
    @property
    def esta_retrasado(self):
        """
        Indica si la devolución está retrasada.
        """
        hoy = timezone.now().date()
        return (self.fecha_devolucion is None and 
                hoy > self.fecha_fin_prevista)
    
    @property
    def dias_retraso(self):
        """
        Calcula los días de retraso en la devolución.
        """
        if not self.esta_retrasado:
            return 0
        hoy = timezone.now().date()
        return (hoy - self.fecha_fin_prevista).days


class DetalleAlquiler(BaseModel):
    """
    Detalle de los recursos incluidos en un alquiler.
    """
    alquiler = models.ForeignKey(Alquiler, verbose_name=_("Alquiler"),
                                on_delete=models.CASCADE, related_name="detalles")
    recurso = models.ForeignKey(Recurso, verbose_name=_("Recurso"),
                               on_delete=models.PROTECT, related_name="detalles_alquiler")
    cantidad = models.PositiveIntegerField(_("Cantidad"), default=1)
    precio_unitario = models.DecimalField(_("Precio unitario"), max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(0)])
    deposito_unitario = models.DecimalField(_("Depósito unitario"), max_digits=10, decimal_places=2,
                                           default=0, validators=[MinValueValidator(0)])
    notas = models.TextField(_("Notas"), blank=True)
    
    # Estado de devolución
    devuelto = models.BooleanField(_("Devuelto"), default=False)
    fecha_devolucion = models.DateField(_("Fecha de devolución"), null=True, blank=True)
    estado_devolucion = models.TextField(_("Estado en devolución"), blank=True,
                                        help_text=_("Descripción del estado del recurso al ser devuelto"))
    
    class Meta:
        verbose_name = _("Detalle de alquiler")
        verbose_name_plural = _("Detalles de alquiler")
        ordering = ['alquiler', 'id']
        unique_together = [['alquiler', 'recurso']]
    
    def __str__(self):
        return f"{self.recurso.nombre} ({self.cantidad}) - {self.alquiler.codigo}"
    
    @property
    def subtotal(self):
        """
        Calcula el subtotal del detalle (precio * cantidad).
        """
        return self.precio_unitario * self.cantidad
    
    @property
    def deposito_total(self):
        """
        Calcula el depósito total del detalle (depósito * cantidad).
        """
        return self.deposito_unitario * self.cantidad


class Penalizacion(BaseModel):
    """
    Registro de penalizaciones aplicadas a alquileres por retrasos, daños, etc.
    """
    alquiler = models.ForeignKey(Alquiler, verbose_name=_("Alquiler"),
                                on_delete=models.CASCADE, related_name="penalizaciones")
    detalle = models.ForeignKey(DetalleAlquiler, verbose_name=_("Detalle de alquiler"),
                               on_delete=models.CASCADE, related_name="penalizaciones",
                               null=True, blank=True)
    motivo = models.CharField(_("Motivo"), max_length=200)
    descripcion = models.TextField(_("Descripción"))
    monto = models.DecimalField(_("Monto"), max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(0)])
    fecha = models.DateField(_("Fecha"), default=timezone.now)
    aplicada_por = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Aplicada por"),
                                    on_delete=models.PROTECT, related_name="penalizaciones_aplicadas")
    pagada = models.BooleanField(_("Pagada"), default=False)
    fecha_pago = models.DateField(_("Fecha de pago"), null=True, blank=True)
    
    class Meta:
        verbose_name = _("Penalización")
        verbose_name_plural = _("Penalizaciones")
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Penalización {self.motivo} - {self.alquiler.codigo}"


class ReservaRecurso(BaseModel):
    """
    Reservas anticipadas de recursos para alquiler futuro.
    """
    socio = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Socio"),
                             on_delete=models.CASCADE, related_name="reservas")
    recurso = models.ForeignKey(Recurso, verbose_name=_("Recurso"),
                               on_delete=models.PROTECT, related_name="reservas")
    cantidad = models.PositiveIntegerField(_("Cantidad"), default=1)
    fecha_reserva = models.DateTimeField(_("Fecha de reserva"), auto_now_add=True)
    fecha_inicio = models.DateField(_("Fecha de inicio"))
    fecha_fin = models.DateField(_("Fecha de fin"))
    notas = models.TextField(_("Notas"), blank=True)
    confirmada = models.BooleanField(_("Confirmada"), default=False)
    alquiler = models.ForeignKey(Alquiler, verbose_name=_("Alquiler"),
                                on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="reservas_origen")
    
    class Meta:
        verbose_name = _("Reserva de recurso")
        verbose_name_plural = _("Reservas de recursos")
        ordering = ['-fecha_reserva']
    
    def __str__(self):
        return f"Reserva de {self.recurso.nombre} para {self.socio.username}"
    
    @property
    def esta_vigente(self):
        """
        Indica si la reserva está vigente (no ha pasado la fecha de inicio).
        """
        return timezone.now().date() <= self.fecha_inicio
    
    def convertir_a_alquiler(self):
        """
        Convierte la reserva en un alquiler efectivo.
        """
        # Esta lógica se implementará en las vistas
        pass

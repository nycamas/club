from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from apps.common.models import BaseModel
from django.conf import settings


class Categoria(BaseModel):
    """
    Modelo para categorizar los recursos del club.
    Permite organizar los recursos en grupos lógicos según su tipo o uso.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    icono = models.CharField(_("Icono"), max_length=50, blank=True, help_text=_("Nombre del icono de Bootstrap"))
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    parent = models.ForeignKey('self', verbose_name=_("Categoría padre"), on_delete=models.CASCADE, 
                              null=True, blank=True, related_name="subcategorias")
    
    class Meta:
        verbose_name = _("Categoría")
        verbose_name_plural = _("Categorías")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class TipoRecurso(BaseModel):
    """
    Define los diferentes tipos de recursos que puede manejar el club.
    Ejemplos: Libros, Equipamiento deportivo, Herramientas, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    alquilable = models.BooleanField(_("Alquilable"), default=True, 
                                    help_text=_("Indica si este tipo de recurso puede ser alquilado"))
    vendible = models.BooleanField(_("Vendible"), default=True, 
                                  help_text=_("Indica si este tipo de recurso puede ser vendido"))
    requiere_devolucion = models.BooleanField(_("Requiere devolución"), default=True,
                                             help_text=_("Indica si este tipo de recurso debe ser devuelto tras su alquiler"))
    tiempo_max_alquiler = models.PositiveIntegerField(_("Tiempo máximo de alquiler (días)"), 
                                                     default=30, null=True, blank=True)
    
    class Meta:
        verbose_name = _("Tipo de recurso")
        verbose_name_plural = _("Tipos de recursos")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class EstadoRecurso(BaseModel):
    """
    Define los posibles estados de un recurso.
    Ejemplos: Disponible, Alquilado, En mantenimiento, Reservado, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=50)
    descripcion = models.TextField(_("Descripción"), blank=True)
    disponible = models.BooleanField(_("Disponible para uso"), default=True,
                                    help_text=_("Indica si un recurso en este estado está disponible para alquiler o venta"))
    color = models.CharField(_("Color"), max_length=20, default="primary", 
                            help_text=_("Clase de color de Bootstrap (primary, success, danger, etc.)"))
    
    class Meta:
        verbose_name = _("Estado de recurso")
        verbose_name_plural = _("Estados de recursos")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Recurso(BaseModel):
    """
    Modelo principal para los recursos del club que pueden ser alquilados o vendidos.
    Representa cualquier objeto físico o digital que el club ofrece a sus socios.
    """
    codigo = models.CharField(_("Código"), max_length=50, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=200)
    descripcion = models.TextField(_("Descripción"))
    imagen = models.ImageField(_("Imagen"), upload_to="recursos/", null=True, blank=True)
    
    # Clasificación
    categoria = models.ForeignKey(Categoria, verbose_name=_("Categoría"), 
                                 on_delete=models.PROTECT, related_name="recursos")
    tipo = models.ForeignKey(TipoRecurso, verbose_name=_("Tipo de recurso"), 
                            on_delete=models.PROTECT, related_name="recursos")
    
    # Estado y disponibilidad
    estado = models.ForeignKey(EstadoRecurso, verbose_name=_("Estado"), 
                              on_delete=models.PROTECT, related_name="recursos")
    cantidad_total = models.PositiveIntegerField(_("Cantidad total"), default=1,
                                               help_text=_("Número total de unidades de este recurso"))
    cantidad_disponible = models.PositiveIntegerField(_("Cantidad disponible"), default=1)
    
    # Precios y condiciones
    precio_alquiler = models.DecimalField(_("Precio de alquiler"), max_digits=10, decimal_places=2, 
                                         null=True, blank=True, validators=[MinValueValidator(0)])
    precio_venta = models.DecimalField(_("Precio de venta"), max_digits=10, decimal_places=2, 
                                      null=True, blank=True, validators=[MinValueValidator(0)])
    deposito_garantia = models.DecimalField(_("Depósito de garantía"), max_digits=10, decimal_places=2, 
                                           default=0, validators=[MinValueValidator(0)])
    
    # Metadatos
    fecha_adquisicion = models.DateField(_("Fecha de adquisición"), null=True, blank=True)
    valor_adquisicion = models.DecimalField(_("Valor de adquisición"), max_digits=10, decimal_places=2, 
                                           null=True, blank=True, validators=[MinValueValidator(0)])
    proveedor = models.CharField(_("Proveedor"), max_length=200, blank=True)
    notas = models.TextField(_("Notas adicionales"), blank=True)
    
    # Restricciones
    solo_socios = models.BooleanField(_("Solo para socios"), default=False,
                                     help_text=_("Indica si este recurso solo está disponible para socios"))
    requiere_autorizacion = models.BooleanField(_("Requiere autorización"), default=False,
                                               help_text=_("Indica si se requiere autorización especial para su uso"))
    
    class Meta:
        verbose_name = _("Recurso")
        verbose_name_plural = _("Recursos")
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    def actualizar_disponibilidad(self):
        """
        Actualiza la cantidad disponible basada en alquileres y reservas activas.
        """
        # Esta lógica se implementará cuando tengamos los modelos de alquiler
        pass
    
    @property
    def disponible(self):
        """
        Indica si el recurso está disponible para alquiler o venta.
        """
        return self.estado.disponible and self.cantidad_disponible > 0
    
    @property
    def es_alquilable(self):
        """
        Indica si el recurso puede ser alquilado.
        """
        return self.tipo.alquilable and self.precio_alquiler is not None
    
    @property
    def es_vendible(self):
        """
        Indica si el recurso puede ser vendido.
        """
        return self.tipo.vendible and self.precio_venta is not None


class ImagenRecurso(BaseModel):
    """
    Imágenes adicionales para un recurso.
    """
    recurso = models.ForeignKey(Recurso, verbose_name=_("Recurso"), 
                               on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(_("Imagen"), upload_to="recursos/galerias/")
    titulo = models.CharField(_("Título"), max_length=100, blank=True)
    orden = models.PositiveSmallIntegerField(_("Orden"), default=0)
    
    class Meta:
        verbose_name = _("Imagen de recurso")
        verbose_name_plural = _("Imágenes de recursos")
        ordering = ['recurso', 'orden']
    
    def __str__(self):
        return f"Imagen {self.orden} de {self.recurso.nombre}"


class MantenimientoRecurso(BaseModel):
    """
    Registro de mantenimientos realizados a los recursos.
    """
    recurso = models.ForeignKey(Recurso, verbose_name=_("Recurso"), 
                               on_delete=models.CASCADE, related_name="mantenimientos")
    fecha_inicio = models.DateField(_("Fecha de inicio"))
    fecha_fin = models.DateField(_("Fecha de finalización"), null=True, blank=True)
    descripcion = models.TextField(_("Descripción del mantenimiento"))
    costo = models.DecimalField(_("Costo"), max_digits=10, decimal_places=2, 
                               null=True, blank=True, validators=[MinValueValidator(0)])
    realizado_por = models.CharField(_("Realizado por"), max_length=200)
    estado_anterior = models.ForeignKey(EstadoRecurso, verbose_name=_("Estado anterior"), 
                                       on_delete=models.PROTECT, related_name="+", null=True, blank=True)
    notas = models.TextField(_("Notas adicionales"), blank=True)
    
    class Meta:
        verbose_name = _("Mantenimiento de recurso")
        verbose_name_plural = _("Mantenimientos de recursos")
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        return f"Mantenimiento de {self.recurso.nombre} ({self.fecha_inicio})"


class EtiquetaRecurso(BaseModel):
    """
    Etiquetas para clasificar recursos de manera flexible.
    """
    nombre = models.CharField(_("Nombre"), max_length=50, unique=True)
    descripcion = models.TextField(_("Descripción"), blank=True)
    
    class Meta:
        verbose_name = _("Etiqueta de recurso")
        verbose_name_plural = _("Etiquetas de recursos")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


# Relación muchos a muchos entre Recurso y EtiquetaRecurso
Recurso.etiquetas = models.ManyToManyField(
    EtiquetaRecurso,
    verbose_name=_("Etiquetas"),
    related_name="recursos",
    blank=True
)

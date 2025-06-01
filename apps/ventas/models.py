from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.common.models import BaseModel
from apps.recursos.models import Recurso
from django.conf import settings


class CategoriaProducto(BaseModel):
    """
    Categorías específicas para productos en venta.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    icono = models.CharField(_("Icono"), max_length=50, blank=True, help_text=_("Nombre del icono de Bootstrap"))
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    parent = models.ForeignKey('self', verbose_name=_("Categoría padre"), on_delete=models.CASCADE, 
                              null=True, blank=True, related_name="subcategorias")
    
    class Meta:
        verbose_name = _("Categoría de producto")
        verbose_name_plural = _("Categorías de productos")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Producto(BaseModel):
    """
    Modelo para productos disponibles para venta.
    Puede estar relacionado con un recurso o ser un producto independiente.
    """
    # Identificación
    codigo = models.CharField(_("Código"), max_length=50, unique=True)
    nombre = models.CharField(_("Nombre"), max_length=200)
    descripcion = models.TextField(_("Descripción"))
    imagen = models.ImageField(_("Imagen"), upload_to="productos/", null=True, blank=True)
    
    # Clasificación
    categoria = models.ForeignKey(CategoriaProducto, verbose_name=_("Categoría"), 
                                 on_delete=models.PROTECT, related_name="productos")
    recurso = models.ForeignKey(Recurso, verbose_name=_("Recurso asociado"), 
                               on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name="productos")
    
    # Precios y stock
    precio = models.DecimalField(_("Precio"), max_digits=10, decimal_places=2, 
                                validators=[MinValueValidator(0)])
    precio_oferta = models.DecimalField(_("Precio de oferta"), max_digits=10, decimal_places=2, 
                                       null=True, blank=True, validators=[MinValueValidator(0)])
    stock = models.PositiveIntegerField(_("Stock"), default=0)
    stock_minimo = models.PositiveIntegerField(_("Stock mínimo"), default=5)
    
    # Metadatos
    destacado = models.BooleanField(_("Destacado"), default=False)
    fecha_publicacion = models.DateField(_("Fecha de publicación"), default=timezone.now)
    solo_socios = models.BooleanField(_("Solo para socios"), default=False)
    
    # Detalles adicionales
    marca = models.CharField(_("Marca"), max_length=100, blank=True)
    modelo = models.CharField(_("Modelo"), max_length=100, blank=True)
    peso = models.DecimalField(_("Peso (kg)"), max_digits=6, decimal_places=2, 
                              null=True, blank=True, validators=[MinValueValidator(0)])
    dimensiones = models.CharField(_("Dimensiones"), max_length=100, blank=True, 
                                  help_text=_("Formato: largo x ancho x alto"))
    
    class Meta:
        verbose_name = _("Producto")
        verbose_name_plural = _("Productos")
        ordering = ['nombre']
    
    def __str__(self):
        return f"{self.codigo} - {self.nombre}"
    
    @property
    def disponible(self):
        """
        Indica si el producto está disponible para venta.
        """
        return self.is_active and self.stock > 0
    
    @property
    def precio_actual(self):
        """
        Devuelve el precio actual (oferta o regular).
        """
        if self.precio_oferta and self.precio_oferta < self.precio:
            return self.precio_oferta
        return self.precio
    
    @property
    def porcentaje_descuento(self):
        """
        Calcula el porcentaje de descuento si hay precio de oferta.
        """
        if not self.precio_oferta or self.precio_oferta >= self.precio:
            return 0
        return int(100 - (self.precio_oferta * 100 / self.precio))
    
    @property
    def necesita_reposicion(self):
        """
        Indica si el producto necesita reposición de stock.
        """
        return self.stock <= self.stock_minimo


class ImagenProducto(BaseModel):
    """
    Imágenes adicionales para un producto.
    """
    producto = models.ForeignKey(Producto, verbose_name=_("Producto"), 
                                on_delete=models.CASCADE, related_name="imagenes")
    imagen = models.ImageField(_("Imagen"), upload_to="productos/galerias/")
    titulo = models.CharField(_("Título"), max_length=100, blank=True)
    orden = models.PositiveSmallIntegerField(_("Orden"), default=0)
    
    class Meta:
        verbose_name = _("Imagen de producto")
        verbose_name_plural = _("Imágenes de productos")
        ordering = ['producto', 'orden']
    
    def __str__(self):
        return f"Imagen {self.orden} de {self.producto.nombre}"


class EstadoVenta(BaseModel):
    """
    Define los posibles estados de una venta.
    Ejemplos: Pendiente, Pagada, Enviada, Completada, Cancelada, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=50)
    descripcion = models.TextField(_("Descripción"), blank=True)
    color = models.CharField(_("Color"), max_length=20, default="primary",
                            help_text=_("Clase de color de Bootstrap (primary, success, danger, etc.)"))
    
    class Meta:
        verbose_name = _("Estado de venta")
        verbose_name_plural = _("Estados de venta")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class MetodoPago(BaseModel):
    """
    Métodos de pago disponibles para ventas.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    activo = models.BooleanField(_("Activo"), default=True)
    icono = models.CharField(_("Icono"), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _("Método de pago")
        verbose_name_plural = _("Métodos de pago")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Venta(BaseModel):
    """
    Modelo principal para gestionar las ventas de productos.
    """
    # Identificación y relaciones
    codigo = models.CharField(_("Código"), max_length=50, unique=True)
    cliente = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Cliente"),
                               on_delete=models.PROTECT, related_name="compras")
    
    # Fechas
    fecha_venta = models.DateTimeField(_("Fecha de venta"), auto_now_add=True)
    fecha_pago = models.DateTimeField(_("Fecha de pago"), null=True, blank=True)
    
    # Estado y seguimiento
    estado = models.ForeignKey(EstadoVenta, verbose_name=_("Estado"),
                              on_delete=models.PROTECT, related_name="ventas")
    notas = models.TextField(_("Notas"), blank=True)
    
    # Costos
    subtotal = models.DecimalField(_("Subtotal"), max_digits=10, decimal_places=2,
                                  validators=[MinValueValidator(0)])
    impuestos = models.DecimalField(_("Impuestos"), max_digits=10, decimal_places=2,
                                   default=0, validators=[MinValueValidator(0)])
    descuento = models.DecimalField(_("Descuento"), max_digits=10, decimal_places=2,
                                   default=0, validators=[MinValueValidator(0)])
    total = models.DecimalField(_("Total"), max_digits=10, decimal_places=2,
                               validators=[MinValueValidator(0)])
    
    # Pago
    metodo_pago = models.ForeignKey(MetodoPago, verbose_name=_("Método de pago"),
                                   on_delete=models.PROTECT, related_name="ventas",
                                   null=True, blank=True)
    referencia_pago = models.CharField(_("Referencia de pago"), max_length=100, blank=True)
    
    # Gestión
    vendedor = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Vendedor"),
                                on_delete=models.PROTECT, related_name="ventas_realizadas",
                                null=True, blank=True)
    
    class Meta:
        verbose_name = _("Venta")
        verbose_name_plural = _("Ventas")
        ordering = ['-fecha_venta']
    
    def __str__(self):
        return f"Venta {self.codigo} - {self.cliente.username}"
    
    def calcular_total(self):
        """
        Calcula el total de la venta basado en los detalles.
        """
        self.subtotal = sum(detalle.subtotal for detalle in self.detalles.all())
        self.total = self.subtotal + self.impuestos - self.descuento
        return self.total


class DetalleVenta(BaseModel):
    """
    Detalle de los productos incluidos en una venta.
    """
    venta = models.ForeignKey(Venta, verbose_name=_("Venta"),
                             on_delete=models.CASCADE, related_name="detalles")
    producto = models.ForeignKey(Producto, verbose_name=_("Producto"),
                                on_delete=models.PROTECT, related_name="detalles_venta")
    cantidad = models.PositiveIntegerField(_("Cantidad"), default=1)
    precio_unitario = models.DecimalField(_("Precio unitario"), max_digits=10, decimal_places=2,
                                         validators=[MinValueValidator(0)])
    descuento_unitario = models.DecimalField(_("Descuento unitario"), max_digits=10, decimal_places=2,
                                            default=0, validators=[MinValueValidator(0)])
    notas = models.TextField(_("Notas"), blank=True)
    
    class Meta:
        verbose_name = _("Detalle de venta")
        verbose_name_plural = _("Detalles de venta")
        ordering = ['venta', 'id']
        unique_together = [['venta', 'producto']]
    
    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad}) - {self.venta.codigo}"
    
    @property
    def subtotal(self):
        """
        Calcula el subtotal del detalle (precio * cantidad - descuento).
        """
        return (self.precio_unitario * self.cantidad) - self.descuento_unitario


class Carrito(BaseModel):
    """
    Carrito de compras temporal para usuarios.
    """
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("Usuario"),
                                  on_delete=models.CASCADE, related_name="carrito")
    fecha_creacion = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(_("Fecha de actualización"), auto_now=True)
    
    class Meta:
        verbose_name = _("Carrito")
        verbose_name_plural = _("Carritos")
        ordering = ['-fecha_actualizacion']
    
    def __str__(self):
        return f"Carrito de {self.usuario.username}"
    
    @property
    def total_items(self):
        """
        Cuenta el número total de items en el carrito.
        """
        return sum(item.cantidad for item in self.items.all())
    
    @property
    def subtotal(self):
        """
        Calcula el subtotal del carrito.
        """
        return sum(item.subtotal for item in self.items.all())
    
    def convertir_a_venta(self):
        """
        Convierte el carrito en una venta efectiva.
        """
        # Esta lógica se implementará en las vistas
        pass


class ItemCarrito(BaseModel):
    """
    Item individual en el carrito de compras.
    """
    carrito = models.ForeignKey(Carrito, verbose_name=_("Carrito"),
                               on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, verbose_name=_("Producto"),
                                on_delete=models.CASCADE, related_name="items_carrito")
    cantidad = models.PositiveIntegerField(_("Cantidad"), default=1)
    fecha_agregado = models.DateTimeField(_("Fecha agregado"), auto_now_add=True)
    
    class Meta:
        verbose_name = _("Item de carrito")
        verbose_name_plural = _("Items de carrito")
        ordering = ['-fecha_agregado']
        unique_together = [['carrito', 'producto']]
    
    def __str__(self):
        return f"{self.producto.nombre} ({self.cantidad}) - {self.carrito}"
    
    @property
    def subtotal(self):
        """
        Calcula el subtotal del item (precio actual * cantidad).
        """
        return self.producto.precio_actual * self.cantidad

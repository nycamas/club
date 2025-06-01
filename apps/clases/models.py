from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.common.models import BaseModel
from django.conf import settings


class CategoriaClase(BaseModel):
    """
    Categorías para clasificar los tipos de clases ofrecidas.
    Ejemplos: Deportes, Arte, Música, Idiomas, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=100)
    descripcion = models.TextField(_("Descripción"), blank=True)
    icono = models.CharField(_("Icono"), max_length=50, blank=True, help_text=_("Nombre del icono de Bootstrap"))
    slug = models.SlugField(_("Slug"), max_length=100, unique=True)
    color = models.CharField(_("Color"), max_length=20, default="primary",
                            help_text=_("Clase de color de Bootstrap (primary, success, danger, etc.)"))
    
    class Meta:
        verbose_name = _("Categoría de clase")
        verbose_name_plural = _("Categorías de clases")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre


class Instructor(BaseModel):
    """
    Modelo para los instructores que imparten clases en el club.
    """
    usuario = models.OneToOneField(settings.AUTH_USER_MODEL, verbose_name=_("Usuario"),
                                  on_delete=models.CASCADE, related_name="perfil_instructor")
    biografia = models.TextField(_("Biografía"))
    especialidades = models.TextField(_("Especialidades"))
    foto = models.ImageField(_("Foto"), upload_to="instructores/", null=True, blank=True)
    telefono = models.CharField(_("Teléfono"), max_length=20, blank=True)
    email_contacto = models.EmailField(_("Email de contacto"), blank=True)
    sitio_web = models.URLField(_("Sitio web"), blank=True)
    redes_sociales = models.JSONField(_("Redes sociales"), default=dict, blank=True)
    calificacion = models.DecimalField(_("Calificación promedio"), max_digits=3, decimal_places=2,
                                      null=True, blank=True, validators=[MinValueValidator(0)])
    
    class Meta:
        verbose_name = _("Instructor")
        verbose_name_plural = _("Instructores")
        ordering = ['usuario__last_name', 'usuario__first_name']
    
    def __str__(self):
        return f"{self.usuario.get_full_name()}"
    
    @property
    def nombre_completo(self):
        """
        Devuelve el nombre completo del instructor.
        """
        return self.usuario.get_full_name()


class NivelClase(BaseModel):
    """
    Niveles de dificultad o experiencia para las clases.
    Ejemplos: Principiante, Intermedio, Avanzado, etc.
    """
    nombre = models.CharField(_("Nombre"), max_length=50)
    descripcion = models.TextField(_("Descripción"), blank=True)
    orden = models.PositiveSmallIntegerField(_("Orden"), default=0)
    
    class Meta:
        verbose_name = _("Nivel de clase")
        verbose_name_plural = _("Niveles de clase")
        ordering = ['orden', 'nombre']
    
    def __str__(self):
        return self.nombre


class Clase(BaseModel):
    """
    Modelo principal para las clases ofrecidas por el club.
    """
    # Información básica
    nombre = models.CharField(_("Nombre"), max_length=200)
    descripcion = models.TextField(_("Descripción"))
    categoria = models.ForeignKey(CategoriaClase, verbose_name=_("Categoría"),
                                 on_delete=models.PROTECT, related_name="clases")
    nivel = models.ForeignKey(NivelClase, verbose_name=_("Nivel"),
                             on_delete=models.PROTECT, related_name="clases")
    imagen = models.ImageField(_("Imagen"), upload_to="clases/", null=True, blank=True)
    
    # Detalles
    duracion_minutos = models.PositiveIntegerField(_("Duración (minutos)"), default=60)
    capacidad_maxima = models.PositiveIntegerField(_("Capacidad máxima"), default=10)
    precio = models.DecimalField(_("Precio por sesión"), max_digits=10, decimal_places=2,
                                validators=[MinValueValidator(0)])
    materiales_necesarios = models.TextField(_("Materiales necesarios"), blank=True)
    requisitos_previos = models.TextField(_("Requisitos previos"), blank=True)
    
    # Restricciones
    solo_socios = models.BooleanField(_("Solo para socios"), default=True)
    edad_minima = models.PositiveSmallIntegerField(_("Edad mínima"), null=True, blank=True)
    edad_maxima = models.PositiveSmallIntegerField(_("Edad máxima"), null=True, blank=True)
    
    # Estado
    activa = models.BooleanField(_("Activa"), default=True)
    destacada = models.BooleanField(_("Destacada"), default=False)
    
    class Meta:
        verbose_name = _("Clase")
        verbose_name_plural = _("Clases")
        ordering = ['nombre']
    
    def __str__(self):
        return self.nombre
    
    @property
    def plazas_disponibles(self):
        """
        Calcula el número de plazas disponibles en todas las sesiones futuras.
        """
        # Esta lógica se implementará cuando tengamos las sesiones
        return 0


class SesionClase(BaseModel):
    """
    Sesiones programadas para una clase específica.
    """
    clase = models.ForeignKey(Clase, verbose_name=_("Clase"),
                             on_delete=models.CASCADE, related_name="sesiones")
    instructor = models.ForeignKey(Instructor, verbose_name=_("Instructor"),
                                  on_delete=models.PROTECT, related_name="sesiones")
    fecha = models.DateField(_("Fecha"))
    hora_inicio = models.TimeField(_("Hora de inicio"))
    hora_fin = models.TimeField(_("Hora de fin"))
    ubicacion = models.CharField(_("Ubicación"), max_length=200)
    notas = models.TextField(_("Notas"), blank=True)
    capacidad_maxima = models.PositiveIntegerField(_("Capacidad máxima"), null=True, blank=True,
                                                  help_text=_("Si se deja en blanco, se usa la capacidad de la clase"))
    precio_especial = models.DecimalField(_("Precio especial"), max_digits=10, decimal_places=2,
                                         null=True, blank=True, validators=[MinValueValidator(0)],
                                         help_text=_("Si se deja en blanco, se usa el precio de la clase"))
    cancelada = models.BooleanField(_("Cancelada"), default=False)
    motivo_cancelacion = models.TextField(_("Motivo de cancelación"), blank=True)
    
    class Meta:
        verbose_name = _("Sesión de clase")
        verbose_name_plural = _("Sesiones de clase")
        ordering = ['fecha', 'hora_inicio']
    
    def __str__(self):
        return f"{self.clase.nombre} - {self.fecha} {self.hora_inicio}"
    
    @property
    def duracion_minutos(self):
        """
        Calcula la duración de la sesión en minutos.
        """
        inicio = timezone.datetime.combine(timezone.now().date(), self.hora_inicio)
        fin = timezone.datetime.combine(timezone.now().date(), self.hora_fin)
        duracion = fin - inicio
        return duracion.seconds // 60
    
    @property
    def precio_final(self):
        """
        Devuelve el precio final de la sesión (especial o regular).
        """
        return self.precio_especial if self.precio_especial is not None else self.clase.precio
    
    @property
    def capacidad_final(self):
        """
        Devuelve la capacidad final de la sesión (específica o de la clase).
        """
        return self.capacidad_maxima if self.capacidad_maxima is not None else self.clase.capacidad_maxima
    
    @property
    def plazas_disponibles(self):
        """
        Calcula el número de plazas disponibles en la sesión.
        """
        inscritos = self.inscripciones.filter(cancelada=False).count()
        return max(0, self.capacidad_final - inscritos)
    
    @property
    def completa(self):
        """
        Indica si la sesión está completa (sin plazas disponibles).
        """
        return self.plazas_disponibles == 0


class InscripcionClase(BaseModel):
    """
    Inscripciones de socios a sesiones de clase.
    """
    socio = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Socio"),
                             on_delete=models.CASCADE, related_name="inscripciones_clase")
    sesion = models.ForeignKey(SesionClase, verbose_name=_("Sesión"),
                              on_delete=models.CASCADE, related_name="inscripciones")
    fecha_inscripcion = models.DateTimeField(_("Fecha de inscripción"), auto_now_add=True)
    precio_pagado = models.DecimalField(_("Precio pagado"), max_digits=10, decimal_places=2,
                                       validators=[MinValueValidator(0)])
    pagado = models.BooleanField(_("Pagado"), default=False)
    fecha_pago = models.DateTimeField(_("Fecha de pago"), null=True, blank=True)
    asistio = models.BooleanField(_("Asistió"), null=True, blank=True)
    cancelada = models.BooleanField(_("Cancelada"), default=False)
    fecha_cancelacion = models.DateTimeField(_("Fecha de cancelación"), null=True, blank=True)
    motivo_cancelacion = models.TextField(_("Motivo de cancelación"), blank=True)
    reembolsado = models.BooleanField(_("Reembolsado"), default=False)
    
    class Meta:
        verbose_name = _("Inscripción a clase")
        verbose_name_plural = _("Inscripciones a clases")
        ordering = ['-fecha_inscripcion']
        unique_together = [['socio', 'sesion']]
    
    def __str__(self):
        return f"{self.socio.username} - {self.sesion}"
    
    def cancelar(self, motivo=""):
        """
        Cancela la inscripción a la clase.
        """
        self.cancelada = True
        self.fecha_cancelacion = timezone.now()
        self.motivo_cancelacion = motivo
        self.save()


class ValoracionClase(BaseModel):
    """
    Valoraciones y comentarios de los socios sobre las clases.
    """
    socio = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name=_("Socio"),
                             on_delete=models.CASCADE, related_name="valoraciones_clase")
    clase = models.ForeignKey(Clase, verbose_name=_("Clase"),
                             on_delete=models.CASCADE, related_name="valoraciones")
    sesion = models.ForeignKey(SesionClase, verbose_name=_("Sesión"),
                              on_delete=models.SET_NULL, null=True, blank=True,
                              related_name="valoraciones")
    instructor = models.ForeignKey(Instructor, verbose_name=_("Instructor"),
                                  on_delete=models.SET_NULL, null=True, blank=True,
                                  related_name="valoraciones")
    puntuacion = models.PositiveSmallIntegerField(_("Puntuación"), validators=[MinValueValidator(1)],
                                                 help_text=_("Puntuación de 1 a 5"))
    comentario = models.TextField(_("Comentario"), blank=True)
    fecha = models.DateTimeField(_("Fecha"), auto_now_add=True)
    aprobado = models.BooleanField(_("Aprobado"), default=True,
                                  help_text=_("Indica si el comentario ha sido aprobado para su visualización pública"))
    
    class Meta:
        verbose_name = _("Valoración de clase")
        verbose_name_plural = _("Valoraciones de clases")
        ordering = ['-fecha']
        unique_together = [['socio', 'clase', 'sesion']]
    
    def __str__(self):
        return f"{self.socio.username} - {self.clase.nombre} ({self.puntuacion}★)"

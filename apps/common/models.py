from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría de creación y modificación.
    """
    created_at = models.DateTimeField(_("Fecha de creación"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Fecha de actualización"), auto_now=True)

    class Meta:
        abstract = True


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto que implementa borrado lógico en lugar de físico.
    """
    is_active = models.BooleanField(_("Activo"), default=True)
    deleted_at = models.DateTimeField(_("Fecha de eliminación"), null=True, blank=True)

    def delete(self, using=None, keep_parents=False):
        """
        Sobrescribe el método delete para implementar borrado lógico.
        """
        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, using=None, keep_parents=False):
        """
        Método para realizar borrado físico cuando sea necesario.
        """
        return super().delete(using=using, keep_parents=keep_parents)

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, SoftDeleteModel):
    """
    Modelo base que combina auditoría de tiempo y borrado lógico.
    """
    class Meta:
        abstract = True

from django.db import models
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField


class Articulo(models.Model):
    nombre = models.CharField(max_length=255)
    descripcion = models.TextField()
    cantidad = models.PositiveIntegerField()
    asignacion = models.CharField(max_length=255)
    categoria = models.CharField(max_length=255)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    foto = CloudinaryField('image', blank=True, null=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Relación con el usuario que lo creó

    def __str__(self):
        return f"{self.nombre} - {self.usuario.username}"



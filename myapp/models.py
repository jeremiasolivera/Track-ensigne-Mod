from django.db import models

# Create your models here.
class Paciente(models.Model):
    nombre = models.CharField(max_length=100)
    imagen = models.ImageField(upload_to='pacientes/')
    edad = models.PositiveIntegerField()
    informe_medico = models.TextField()

    def __str__(self):
        return self.nombre
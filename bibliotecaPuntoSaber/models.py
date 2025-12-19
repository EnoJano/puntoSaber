from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

# ---------------------------------------------------------
# USUARIO
# ---------------------------------------------------------

class Usuario(AbstractUser):
    ROLES = [
        ('docente', 'Docente'),
        ('alumno', 'Alumno'),
        ('admin', 'Administrador'),
    ]

    ESTADOS = [
        ('activo', 'Activo'),
        ('desactivado', 'Desactivado'),
    ]

    rol = models.CharField(max_length=20, choices=ROLES, default='alumno')
    estado = models.CharField(max_length=20, choices=ESTADOS, default='activo')
    
    def __str__(self):
        return f"{self.username} ({self.rol})"

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"


    # ejemplo: docente debe ver solo sus archivos
    def es_docente(self):
        return self.rol == "docente"

    def es_alumno(self):
        return self.rol == "alumno"

    def es_admin(self):
        return self.rol == "admin"

    def __str__(self):
        return f"{self.username} ({self.rol})"


# ---------------------------------------------------------
# ARCHIVO / RECURSOS
# ---------------------------------------------------------
class Archivo(models.Model):
    docente = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'docente'},  # solo docentes pueden ser dueños
        related_name="archivos_subidos"
    )

    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    archivo = models.FileField(upload_to='archivos/')

    autor = models.CharField(max_length=200, default="Autor desconocido")
    categoria = models.CharField(max_length=100, default="General")

    fecha_subida = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    ESTADOS = [
        ('activo', 'Activo'),
        ('eliminado_docente', 'Eliminado por docente'),
        ('eliminado_admin', 'Eliminado por administrador'),
    ]

    estado = models.CharField(
        max_length=30,
        choices=ESTADOS,
        default='activo'
    )

    def __str__(self):
        return self.titulo


# ---------------------------------------------------------
# CALIFICACIONES DEL ALUMNO
# ---------------------------------------------------------
class Calificacion(models.Model):
    alumno = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        limit_choices_to={'rol': 'alumno'}
    )

    archivo = models.ForeignKey(
        Archivo, 
        on_delete=models.CASCADE, 
        related_name="calificaciones")

    puntaje = models.IntegerField(choices=[
        (1, "1 estrella"),
        (2, "2 estrellas"),
        (3, "3 estrellas"),
        (4, "4 estrellas"),
        (5, "5 estrellas"),
    ])

    comentario = models.TextField(blank=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('alumno', 'archivo')  # un alumno solo puede calificar una vez

    def __str__(self):
        return f"{self.alumno.username} → {self.archivo.titulo} ({self.puntaje})"

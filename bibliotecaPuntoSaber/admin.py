from django.contrib import admin
from .models import Usuario, Archivo, Calificacion
from django.contrib.auth.admin import UserAdmin

# -----------------------------
#   ADMIN PARA USUARIO
# -----------------------------

class UsuarioAdmin(UserAdmin):
    model = Usuario
    list_display = ('username', 'email', 'rol', 'estado', 'is_staff')
    list_filter = ('rol', 'estado', 'is_staff')
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('first_name', 'last_name', 'email')}),
        ('Rol y Estado', {'fields': ('rol', 'estado')}),
        ('Permisos', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username','email', 'password1', 'password2', 'rol', 'estado', 'is_active', 'is_staff')}
        ),
    )
    search_fields = ('username', 'email')
    ordering = ('username',)

admin.site.register(Usuario, UsuarioAdmin)


# -----------------------------
#   ADMIN PARA ARCHIVO
# -----------------------------
@admin.register(Archivo)
class ArchivoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'docente', 'fecha_subida', 'estado')
    list_filter = ('estado', 'docente')
    search_fields = ('titulo', 'descripcion')


# -----------------------------
#   ADMIN PARA CALIFICACIÓN
# -----------------------------
@admin.register(Calificacion)
class CalificacionAdmin(admin.ModelAdmin):
    list_display = ('archivo', 'alumno', 'puntaje', 'fecha')
    list_filter = ('puntaje',)
    search_fields = ('archivo__titulo', 'alumno__username')
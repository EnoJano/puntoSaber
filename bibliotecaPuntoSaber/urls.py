from django.urls import path
from .views import login_view, alumno_home, docente_home
from django.contrib.auth.views import LogoutView
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', login_view, name='login'),
    path('alumno/', alumno_home, name='alumno_home'),
    path('docente/', docente_home, name='docente_home'),
    path("panel-admin/", views.admin_home, name="admin_home"),
    path("panel-admin/crear-usuario/", views.crear_usuario, name="crear_usuario"),
    path("panel-admin/editar-usuario/<int:usuario_id>/", views.editar_usuario, name="editar_usuario"),
    path("panel-admin/desactivar/<int:user_id>/", views.desactivar_usuario, name="desactivar_usuario"),
    path("panel-admin/activar/<int:user_id>/", views.activar_usuario, name="activar_usuario"),
    path("panel-admin/editar-archivo/<int:archivo_id>/", views.editar_archivo_admin, name="editar_archivo_admin"),
    path("panel-admin/eliminar-archivo/<int:archivo_id>/", views.eliminar_archivo_admin, name="eliminar_archivo_admin"),
    path("panel-admin/restaurar-archivo/<int:archivo_id>/",views.restaurar_archivo_admin,name="restaurar_archivo_admin"),
    path("docente/subir/", views.subir_archivo, name="subir_archivo"),
    path("docente/editar/<int:archivo_id>/", views.editar_archivo, name="editar_archivo"),
    path("docente/eliminar/<int:archivo_id>/", views.eliminar_archivo, name="eliminar_archivo"),
    path("calificar/", views.guardar_calificacion, name="guardar_calificacion"),
    path("archivo/<int:archivo_id>/", views.detalle_archivo, name="detalle_archivo"),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),   
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import Usuario, Archivo, Calificacion
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from django.db.models import Avg
from .forms import UsuarioForm
from django.contrib import messages
from .forms import ArchivoForm
from django.contrib.auth.hashers import make_password


def login_view(request):
    mensaje = None
    tipo_mensaje = None

    if request.method == "POST":
        correo = request.POST.get("correo").strip().lower()
        password = request.POST.get("password").strip()

        if correo == "" or password == "":
            mensaje = "Completa todos los campos"
            tipo_mensaje = "error"
        else:
            # Buscar usuario por correo
            try:
                user = Usuario.objects.get(email=correo)
            except Usuario.DoesNotExist:
                mensaje = "Usuario o contraseña incorrectos"
                tipo_mensaje = "error"
                return render(request, "login.html", {"mensaje": mensaje, "tipo_mensaje": tipo_mensaje})

            # Autenticar
            user = authenticate(request, username=user.username, password=password)

            if user is None:
                mensaje = "Usuario o contraseña incorrectos"
                tipo_mensaje = "error"
            else:
                if user.estado == "desactivado":
                    mensaje = "Tu cuenta está desactivada. Por favor, contacta al administrador."
                    tipo_mensaje = "error"
                else:
                    login(request, user)

                    # Redirigir según rol
                    if user.rol == "admin":
                        return redirect("admin_home")
                    elif user.rol == "docente":
                        return redirect("docente_home")
                    else:
                        return redirect("alumno_home")

    return render(request, "login.html", {"mensaje": mensaje, "tipo_mensaje": tipo_mensaje})

@login_required
def alumno_home(request):

    # Solo alumnos pueden ingresar
    if request.user.rol != "alumno":
        return redirect('login')

    # Lista completa de archivos
    archivos = Archivo.objects.filter(estado="activo")

    # -------------------------------
    # AGRUPAR POR AUTOR
    # -------------------------------
    archivos_por_autor = {}
    for archivo in archivos:
        archivos_por_autor.setdefault(archivo.autor, []).append(archivo)

    # -------------------------------
    # AGRUPAR POR DOCENTE
    # -------------------------------
    archivos_por_docente = {}
    for archivo in archivos:
        nombre_docente = f"{archivo.docente.first_name} {archivo.docente.last_name}".strip()
        if nombre_docente == "":
            nombre_docente = archivo.docente.username
        archivos_por_docente.setdefault(nombre_docente, []).append(archivo)

    # -------------------------------
    # CATEGORÍAS ÚNICAS
    # -------------------------------
    categorias = archivos.values_list("categoria", flat=True).distinct()

    # -------------------------------
    # TODOS LOS LIBROS
    # -------------------------------
    todos_los_archivos = archivos

    contexto = {
        "archivos_por_autor": archivos_por_autor,
        "archivos_por_docente": archivos_por_docente,
        "categorias": categorias,
        "todos_los_archivos": todos_los_archivos,
    }

    return render(request, "alumno_home.html", contexto)

@login_required
def guardar_calificacion(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método no permitido"}, status=405)

    data = json.loads(request.body)

    archivo_id = data.get("archivo_id")
    puntaje = data.get("puntaje")
    comentario = data.get("comentario", "")

    if not archivo_id or not puntaje:
        return JsonResponse({"error": "Datos incompletos"}, status=400)

    archivo = Archivo.objects.get(id=archivo_id)

    # Crear o actualizar calificación
    calificacion, creada = Calificacion.objects.update_or_create(
        alumno=request.user,
        archivo=archivo,
        defaults={
            "puntaje": puntaje,
            "comentario": comentario
        }
    )

    return JsonResponse({
        "mensaje": "Calificación guardada correctamente",
        "puntaje": calificacion.puntaje
    })

@login_required
def detalle_archivo(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id)

    calificaciones = Calificacion.objects.filter(archivo=archivo)

    promedio = calificaciones.aggregate(avg=Avg("puntaje"))["avg"]
    promedio = round(promedio, 1) if promedio else 0

    comentarios = [
        {
            "alumno": c.alumno.username,
            "comentario": c.comentario,
            "puntaje": c.puntaje,
        }
        for c in calificaciones.exclude(comentario="")
    ]

    # Calificación del alumno actual (si existe)
    calificacion_usuario = calificaciones.filter(alumno=request.user).first()

    return JsonResponse({
        "titulo": archivo.titulo,
        "archivo_url": archivo.archivo.url if archivo.archivo else "",
        "promedio": promedio,
        "total_calificaciones": calificaciones.count(),
        "comentarios": comentarios,
        "mi_calificacion": {
            "puntaje": calificacion_usuario.puntaje,
            "comentario": calificacion_usuario.comentario
        } if calificacion_usuario else None
    })

@login_required
def docente_home(request):
    if request.user.rol != "docente":
        return redirect("login")

    archivos = Archivo.objects.filter(
        docente=request.user).exclude(estado="eliminado_docente")

    return render(request, "docente_home.html", {
        "archivos": archivos
    })


@login_required
def subir_archivo(request):
    if request.user.rol != "docente":
        return redirect("login")

    if request.method == "POST":
        form = ArchivoForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.save(commit=False)
            archivo.docente = request.user
            archivo.save()
            return redirect("docente_home")
    else:
        form = ArchivoForm()

    return render(request, "docente_subir.html", {
        "form": form,
        "volver_docente": True
        })

@login_required
def editar_archivo(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id, docente=request.user)

    if request.method == "POST":
        form = ArchivoForm(request.POST, request.FILES, instance=archivo)
        if form.is_valid():
            form.save()
            return redirect("docente_home")
    else:
        form = ArchivoForm(instance=archivo)

    return render(request, "docente_editar.html", {
        "form": form,
        "volver_docente": True})

@login_required
def eliminar_archivo(request, archivo_id):
    archivo = Archivo.objects.get(id=archivo_id, docente=request.user)
    archivo.estado = "eliminado_docente"
    archivo.save()
    return redirect("docente_home")

@login_required
def admin_home(request):
    if request.user.rol != "admin":
        return redirect("login")

    usuarios = Usuario.objects.exclude(rol="admin")
    archivos = Archivo.objects.all()

    return render(request, "admin/admin_home.html", {
        "usuarios": usuarios,
        "archivos": archivos
    })

@login_required
def desactivar_usuario(request, user_id):
    if request.user.rol != "admin":
        return redirect("login")

    usuario = Usuario.objects.get(id=user_id)
    usuario.estado = "desactivado"
    usuario.save()
    return redirect("admin_home")


@login_required
def activar_usuario(request, user_id):
    if request.user.rol != "admin":
        return redirect("login")

    usuario = Usuario.objects.get(id=user_id)
    usuario.estado = "activo"
    usuario.save()
    return redirect("admin_home")

@login_required
def crear_usuario(request):
    if request.user.rol != "admin":
        return redirect("login")

    if request.method == "POST":
        form = UsuarioForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("admin_home")
    else:
        form = UsuarioForm()

    return render(request, "admin_usuario_form.html", {"form": form})

@login_required
def editar_archivo_admin(request, archivo_id):
    if request.user.rol != "admin":
        return redirect("login")

    archivo = get_object_or_404(Archivo, id=archivo_id)

    if request.method == "POST":
        archivo.titulo = request.POST.get("titulo")
        archivo.descripcion = request.POST.get("descripcion")
        archivo.autor = request.POST.get("autor")
        archivo.categoria = request.POST.get("categoria")
        archivo.estado = request.POST.get("estado")

        if request.FILES.get("archivo"):
            archivo.archivo = request.FILES["archivo"]

        archivo.save()
        return redirect("admin_home")

    return render(request, "admin/editar_archivo.html", {
        "archivo": archivo
    })

@login_required
def eliminar_archivo_admin(request, archivo_id):
    if request.user.rol != "admin":
        return redirect("login")

    archivo = Archivo.objects.get(id=archivo_id)

    archivo.estado = "eliminado"
    archivo.save()
    return redirect("admin_home")

@login_required
def restaurar_archivo_admin(request, archivo_id):
    if request.user.rol != "admin":
        return redirect("login")

    archivo = get_object_or_404(Archivo, id=archivo_id)
    archivo.estado = "activo"
    archivo.save()

    return redirect("admin_home")

@login_required
def editar_usuario(request, usuario_id):

    # Solo admin
    if request.user.rol != "admin":
        return redirect("login")

    usuario = get_object_or_404(Usuario, id=usuario_id)

    # 🔒 No permitir editar otros admins desde este panel
    if usuario.rol == "admin":
        return redirect("admin_home")

    if request.method == "POST":
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        rol = request.POST.get("rol")
        estado = request.POST.get("estado")

        # 🔐 Bloquear asignación de rol admin
        if rol == "admin":
            messages.error(
                request,
                "No está permitido asignar rol administrador"
            )
            return redirect("editar_usuario", usuario_id=usuario.id)

        # Validación básica
        if email == "":
            messages.error(request, "El email no puede estar vacío")
            return redirect("editar_usuario", usuario_id=usuario.id)

        # Guardar cambios
        usuario.first_name = first_name
        usuario.last_name = last_name
        usuario.email = email
        usuario.rol = rol
        usuario.estado = estado

        usuario.save()
        messages.success(request, "Usuario actualizado correctamente")

        return redirect("admin_home")

    return render(request, "admin/editar_usuario.html", {
        "usuario": usuario
    })
@login_required
def crear_usuario(request):

    # Solo admin
    if request.user.rol != "admin":
        return redirect("login")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        email = request.POST.get("email", "").strip()
        rol = request.POST.get("rol")
        password = request.POST.get("password")

        # 🔒 Validaciones
        if rol == "admin":
            messages.error(request, "No está permitido crear administradores")
            return redirect("crear_usuario")

        if not all([username, email, password]):
            messages.error(request, "Usuario, email y contraseña son obligatorios")
            return redirect("crear_usuario")

        if Usuario.objects.filter(username=username).exists():
            messages.error(request, "El nombre de usuario ya existe")
            return redirect("crear_usuario")

        if Usuario.objects.filter(email=email).exists():
            messages.error(request, "El email ya está registrado")
            return redirect("crear_usuario")

        # Crear usuario
        Usuario.objects.create(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            rol=rol,
            estado="activo",
            password=make_password(password)
        )

        messages.success(request, "Usuario creado correctamente")
        return redirect("admin_home")

    return render(request, "admin/crear_usuario.html")

@login_required
def editar_archivo_admin(request, archivo_id):

    # Solo admin
    if request.user.rol != "admin":
        return redirect("login")

    archivo = get_object_or_404(Archivo, id=archivo_id)

    if request.method == "POST":
        archivo.titulo = request.POST.get("titulo")
        archivo.descripcion = request.POST.get("descripcion")
        archivo.autor = request.POST.get("autor")
        archivo.categoria = request.POST.get("categoria")
        archivo.estado = request.POST.get("estado")

        # Reemplazar archivo si se sube uno nuevo
        if request.FILES.get("archivo"):
            archivo.archivo = request.FILES["archivo"]

        archivo.save()
        return redirect("admin_home")

    return render(request, "admin/editar_archivo.html", {
        "archivo": archivo
    })

@login_required
def eliminar_archivo_admin(request, archivo_id):

    if request.user.rol != "admin":
        return redirect("login")

    archivo = get_object_or_404(Archivo, id=archivo_id)
    archivo.estado = "eliminado"
    archivo.save()

    return redirect("admin_home")

@login_required
def restaurar_archivo_admin(request, archivo_id):
    if request.user.rol != "admin":
        return redirect("login")

    archivo = get_object_or_404(Archivo, id=archivo_id)
    archivo.estado = "activo"
    archivo.save()

    return redirect("admin_home")
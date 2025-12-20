# puntoSaber
Sistema web de biblioteca académica desarrollado con Django

Punto Saber
Sistema Web de Biblioteca Académica
Sistema web desarrollado con Django que permite la gestión, publicación y visualización de material 
académico en un entorno controlado por roles (Administrador, Docente y Alumno).

Descripción general
Punto Saber es una plataforma pensada para instituciones educativas, donde los docentes pueden subir 
material académico, los alumnos pueden consultarlo y evaluarlo, y los administradores pueden gestionar 
usuarios y contenidos.

El sistema prioriza:
-  Usabilidad
-  Organización del contenido
-  Control de accesos por rol
-  Interfaz clara y moderna

Roles del sistema
Administrador
-  Gestión de usuarios (crear, editar, activar/desactivar)
-  Gestión global de archivos
-  Control del estado de los contenidos
-  Supervisión general del sistema

Docente
-  Subida de archivos académicos
-  Edición y eliminación de sus propios archivos
-  Visualización de calificaciones promedio

Alumno
-  Visualización de archivos disponibles
-  Búsqueda y filtrado de contenidos
-  Visualización de detalles y calificación de archivos

Funcionalidades principales
-  Autenticación y control de acceso por roles
-  CRUD completo de usuarios y archivos
-  Panel de administración personalizado
-  Interfaz moderna con CSS personalizado
-  Sistema de estados para archivos (activo / eliminado)
-  Diseño responsive
-  Validaciones en formularios
-  Estructura preparada para escalar

Tecnologías utilizadas
- Backend
    Python
    Django
- Frontend
    HTML5
    CSS3
    JavaScript
- Base de datos
    SQLite (modo desarrollo)
- Control de versiones
    Git
    GitHub

Estructura del Proyecto
puntoSaber/
│
├── bibliotecaPuntoSaber/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   └── templates/
│
├── staticfiles/
│   ├── css/
│   └── js/
│
├── manage.py
├── README.md
└── .gitignore


Estado actual del proyecto
  - Proyecto Finalizado

Autor
  Alejandro F. Escobedo Miño
  Ingeniero en Informática & Comunicador Audiovisual
  Chile

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import date
from django.db import transaction
from django.contrib.auth.hashers import make_password
from academico.models import (
    Rol, EstadoProyecto, Facultad, Carrera, Materia,
    Usuario, Estudiante, Docente, Proyecto, ProyectoMiembro, Inscripcion
)
from academico.constants import ROLE_ADMIN, ROLE_DOCENTE, ROLE_ESTUDIANTE, PROJECT_ROLE_LEADER

@transaction.atomic
def seed_data():
    print("Iniciando seed de datos iniciales en academico...")

    # 1. Roles
    rol_admin, _ = Rol.objects.get_or_create(
        nombre=ROLE_ADMIN,
        defaults={'descripcion': 'Administrador del sistema académico'}
    )
    rol_docente, _ = Rol.objects.get_or_create(
        nombre=ROLE_DOCENTE,
        defaults={'descripcion': 'Catedrático / Tutor académico'}
    )
    rol_estudiante, _ = Rol.objects.get_or_create(
        nombre=ROLE_ESTUDIANTE,
        defaults={'descripcion': 'Estudiante universitario regular'}
    )

    # 2. Estados de Proyecto
    estado_borrador, _ = EstadoProyecto.objects.get_or_create(nombre='Propuesta / Borrador')
    estado_revision, _ = EstadoProyecto.objects.get_or_create(nombre='En Revisión')
    estado_aprobado, _ = EstadoProyecto.objects.get_or_create(nombre='Aprobado')
    estado_curso, _ = EstadoProyecto.objects.get_or_create(nombre='En Curso')
    estado_finalizado, _ = EstadoProyecto.objects.get_or_create(nombre='Finalizado')

    # 3. Facultades y Carreras
    facultad_ing, _ = Facultad.objects.get_or_create(nombre='Facultad de Ciencias Exactas y Tecnología')
    facultad_cs, _ = Facultad.objects.get_or_create(nombre='Facultad de Ciencias de la Computación')

    carrera_sistemas, _ = Carrera.objects.get_or_create(
        codigo='INF-SIS',
        defaults={
            'nombre': 'Ingeniería de Sistemas',
            'facultad': facultad_cs,
            'institucion': 'Universidad Autónoma Gabriel René Moreno'
        }
    )

    # 4. Materias
    materia_ia, _ = Materia.objects.get_or_create(
        carrera=carrera_sistemas,
        codigo='INF-412',
        defaults={
            'nombre': 'Inteligencia Artificial',
            'creditos': 5,
            'semestre_materia': 7
        }
    )
    materia_bd, _ = Materia.objects.get_or_create(
        carrera=carrera_sistemas,
        codigo='INF-312',
        defaults={
            'nombre': 'Sistemas de Gestión de Base de Datos',
            'creditos': 5,
            'semestre_materia': 5
        }
    )

    # 5. Usuarios (Password: password123)
    user_docente, _ = Usuario.objects.get_or_create(
        username='docente_garcia',
        defaults={
            'password': make_password('password123'),
            'email': 'garcia@universidad.edu',
            'rol': rol_docente,
            'activo': True
        }
    )

    user_estudiante, _ = Usuario.objects.get_or_create(
        username='estudiante_perez',
        defaults={
            'password': make_password('password123'),
            'email': 'perez@universidad.edu',
            'rol': rol_estudiante,
            'activo': True
        }
    )

    # 6. Perfiles Docente y Estudiante
    docente, _ = Docente.objects.get_or_create(
        usuario=user_docente,
        defaults={
            'nombre': 'Dr. Carlos García',
            'especialidad': 'Inteligencia Artificial y Bases de Datos',
            'facultad': facultad_cs.nombre
        }
    )

    estudiante, _ = Estudiante.objects.get_or_create(
        usuario=user_estudiante,
        defaults={
            'nombre': 'Juan Pérez Gómez',
            'registro': '20241001',
            'carrera': carrera_sistemas,
            'semestre': 6,
            'fecha_nacimiento': date(2002, 5, 14),
            'ppa': 8.85
        }
    )

    # 7. Inscripción inicial
    Inscripcion.objects.get_or_create(
        estudiante=estudiante,
        materia=materia_ia
    )

    # 8. Proyecto inicial
    proyecto, _ = Proyecto.objects.get_or_create(
        titulo='Sistema Inteligente de Predicción de Rendimiento Académico',
        defaults={
            'estudiante': estudiante,
            'tutor': docente,
            'descripcion': 'Backend GraphQL con modelos de Deep Learning para retención estudiantil.',
            'estado': estado_curso,
            'fecha_inicio': date(2026, 2, 1)
        }
    )

    ProyectoMiembro.objects.get_or_create(
        proyecto=proyecto,
        estudiante=estudiante,
        defaults={'rol': PROJECT_ROLE_LEADER, 'es_lider': True}
    )

    print("Seed completado exitosamente con roles, materias, docentes, estudiantes y proyectos de prueba.")

if __name__ == '__main__':
    seed_data()

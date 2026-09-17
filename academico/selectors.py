"""
Capa de Selectores (Query Layer).
Responsable exclusiva de consultas, filtrado y optimización de QuerySets en la BD
sin acoplar lógica en los resolutores GraphQL.
"""

from typing import Optional
from django.db.models import QuerySet
from .models import (
    Rol, Facultad, Carrera, Materia, Estudiante, Docente,
    EstadoProyecto, Proyecto, Inscripcion, Auditoria
)


def get_all_roles() -> QuerySet[Rol]:
    return Rol.objects.all().order_by('id')


def get_all_facultades() -> QuerySet[Facultad]:
    return Facultad.objects.all().order_by('nombre')


def get_carreras(facultad_id: Optional[int] = None) -> QuerySet[Carrera]:
    qs = Carrera.objects.select_related('facultad').all().order_by('nombre')
    if facultad_id is not None:
        qs = qs.filter(facultad_id=facultad_id)
    return qs


def get_materias(
    carrera_id: Optional[int] = None,
    semestre: Optional[int] = None
) -> QuerySet[Materia]:
    qs = Materia.objects.select_related('carrera').all().order_by('semestre_materia', 'nombre')
    if carrera_id is not None:
        qs = qs.filter(carrera_id=carrera_id)
    if semestre is not None:
        qs = qs.filter(semestre_materia=semestre)
    return qs


def get_docentes() -> QuerySet[Docente]:
    return Docente.objects.select_related('usuario').all().order_by('nombre')


def get_estados_proyecto() -> QuerySet[EstadoProyecto]:
    return EstadoProyecto.objects.all().order_by('id')


def get_proyectos(
    estado_id: Optional[int] = None,
    tutor_id: Optional[int] = None,
    estudiante_id: Optional[int] = None,
    search_query: Optional[str] = None
) -> QuerySet[Proyecto]:
    qs = Proyecto.objects.select_related(
        'estudiante', 'tutor', 'estado'
    ).prefetch_related(
        'miembros__estudiante'
    ).all().order_by('-id')

    if estado_id is not None:
        qs = qs.filter(estado_id=estado_id)
    if tutor_id is not None:
        qs = qs.filter(tutor_id=tutor_id)
    if estudiante_id is not None:
        qs = qs.filter(estudiante_id=estudiante_id)
    if search_query:
        qs = qs.filter(titulo__icontains=search_query.strip())
    return qs


def get_proyecto_by_id(proyecto_id: int) -> Optional[Proyecto]:
    return Proyecto.objects.select_related(
        'estudiante', 'tutor', 'estado'
    ).prefetch_related(
        'miembros__estudiante'
    ).filter(pk=proyecto_id).first()


def get_estudiantes(
    carrera_id: Optional[int] = None,
    semestre: Optional[int] = None
) -> QuerySet[Estudiante]:
    qs = Estudiante.objects.select_related('usuario', 'carrera').all().order_by('registro')
    if carrera_id is not None:
        qs = qs.filter(carrera_id=carrera_id)
    if semestre is not None:
        qs = qs.filter(semestre=semestre)
    return qs


def get_estudiante_by_id(estudiante_id: int) -> Optional[Estudiante]:
    return Estudiante.objects.select_related('usuario', 'carrera').filter(pk=estudiante_id).first()


def get_estudiante_by_registro(registro: str) -> Optional[Estudiante]:
    return Estudiante.objects.select_related('usuario', 'carrera').filter(registro=registro.strip()).first()


def get_materias_por_estudiante(estudiante: Estudiante) -> QuerySet[Materia]:
    return Materia.objects.filter(inscripciones__estudiante=estudiante).select_related('carrera')


def get_docente_by_id(docente_id: int) -> Optional[Docente]:
    return Docente.objects.select_related('usuario').filter(pk=docente_id).first()


def get_materia_by_id(materia_id: int) -> Optional[Materia]:
    return Materia.objects.select_related('carrera__facultad').filter(pk=materia_id).first()


def get_inscripciones(
    estudiante_id: Optional[int] = None,
    materia_id: Optional[int] = None
) -> QuerySet[Inscripcion]:
    qs = Inscripcion.objects.select_related('estudiante__carrera', 'materia__carrera').all().order_by('-fecha_inscripcion')
    if estudiante_id is not None:
        qs = qs.filter(estudiante_id=estudiante_id)
    if materia_id is not None:
        qs = qs.filter(materia_id=materia_id)
    return qs


def get_auditorias(
    usuario_id: Optional[int] = None,
    tabla: Optional[str] = None,
    accion: Optional[str] = None,
    limit: int = 50
) -> QuerySet[Auditoria]:
    from .models import Auditoria
    qs = Auditoria.objects.select_related('usuario').all().order_by('-fecha')
    if usuario_id is not None:
        qs = qs.filter(usuario_id=usuario_id)
    if tabla:
        qs = qs.filter(tabla__iexact=tabla.strip())
    if accion:
        qs = qs.filter(accion__iexact=accion.strip())
    return qs[:limit]


def get_dashboard_resumen() -> dict:
    from django.db.models import Avg, Count
    from .models import Usuario, Estudiante, Docente, Proyecto, Materia

    return {
        'total_estudiantes': Estudiante.objects.count(),
        'total_docentes': Docente.objects.count(),
        'total_proyectos': Proyecto.objects.count(),
        'total_materias': Materia.objects.count(),
        'promedio_ppa_estudiantes': Estudiante.objects.aggregate(avg_ppa=Avg('ppa'))['avg_ppa'] or 0.0,
    }

"""
Capa de Servicios de Dominio (Business Logic Layer).
Contiene toda la lógica de negocio, transacciones atómicas, validaciones
y auditoría para proyectos e inscripciones.
"""

from datetime import date
from typing import Optional
from django.db import transaction
from django.utils import timezone
from .models import (
    Usuario, Estudiante, Docente, EstadoProyecto,
    Proyecto, ProyectoMiembro, Materia, Inscripcion, Auditoria
)
from .constants import (
    AUDIT_ACTION_CREATE_PROJECT, AUDIT_ACTION_ENROLL_COURSE,
    TABLE_PROYECTOS, TABLE_INSCRIPCIONES, PROJECT_ROLE_LEADER
)
from .exceptions import ResourceNotFoundException, BusinessRuleValidationException


class ProyectoService:
    """Servicio para la orquestación y reglas de negocio de Proyectos."""

    @staticmethod
    @transaction.atomic
    def crear_proyecto(
        user: Usuario,
        titulo: str,
        tutor_id: int,
        descripcion: Optional[str] = None,
        estudiante_id: Optional[int] = None,
        estado_id: Optional[int] = None,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Proyecto:
        # 1. Determinar el estudiante creador
        if estudiante_id is not None:
            try:
                estudiante = Estudiante.objects.select_for_update().get(pk=estudiante_id)
            except Estudiante.DoesNotExist:
                raise ResourceNotFoundException(f"No existe un estudiante con ID {estudiante_id}.")
        else:
            try:
                estudiante = Estudiante.objects.select_for_update().get(usuario=user)
            except Estudiante.DoesNotExist:
                raise BusinessRuleValidationException(
                    "El usuario autenticado no posee un perfil de Estudiante asociado. Indique un 'estudiante_id'."
                )

        # 2. Validar tutor
        try:
            tutor = Docente.objects.get(pk=tutor_id)
        except Docente.DoesNotExist:
            raise ResourceNotFoundException(f"No existe un docente tutor con ID {tutor_id}.")

        # 3. Validar estado
        if estado_id is not None:
            try:
                estado = EstadoProyecto.objects.get(pk=estado_id)
            except EstadoProyecto.DoesNotExist:
                raise ResourceNotFoundException(f"No existe un estado de proyecto con ID {estado_id}.")
        else:
            estado = EstadoProyecto.objects.first()
            if not estado:
                raise BusinessRuleValidationException(
                    "No se encontraron estados configurados en la tabla 'EstadoProyecto'."
                )

        # 4. Validar fechas de proyecto si ambas existen
        inicio = fecha_inicio or timezone.now().date()
        if fecha_fin and fecha_fin < inicio:
            raise BusinessRuleValidationException("La fecha de fin no puede ser anterior a la fecha de inicio.")

        # 5. Crear el proyecto
        proyecto = Proyecto.objects.create(
            estudiante=estudiante,
            tutor=tutor,
            titulo=titulo.strip(),
            descripcion=descripcion.strip() if descripcion else "",
            estado=estado,
            fecha_inicio=inicio,
            fecha_fin=fecha_fin
        )

        # 6. Registrar al estudiante automáticamente como líder en ProyectosMiembros
        ProyectoMiembro.objects.create(
            proyecto=proyecto,
            estudiante=estudiante,
            rol=PROJECT_ROLE_LEADER,
            es_lider=True
        )

        # 7. Registrar auditoría
        Auditoria.objects.create(
            usuario=user,
            accion=AUDIT_ACTION_CREATE_PROJECT,
            tabla=TABLE_PROYECTOS,
            registro_id=proyecto.id,
            detalles=f"Proyecto #{proyecto.id} '{proyecto.titulo}' creado exitosamente."
        )

        return proyecto


class InscripcionService:
    """Servicio para la orquestación y reglas de negocio de Inscripciones."""

    @staticmethod
    @transaction.atomic
    def inscribir_materia(
        estudiante_id: int,
        materia_id: int,
        user: Optional[Usuario] = None
    ) -> Inscripcion:
        # 1. Validar existencia del estudiante
        try:
            estudiante = Estudiante.objects.get(pk=estudiante_id)
        except Estudiante.DoesNotExist:
            raise ResourceNotFoundException(f"No se encontró el estudiante con ID {estudiante_id}.")

        # 2. Validar existencia de la materia
        try:
            materia = Materia.objects.get(pk=materia_id)
        except Materia.DoesNotExist:
            raise ResourceNotFoundException(f"No se encontró la materia con ID {materia_id}.")

        # 3. Regla de negocio: No permitir inscripciones duplicadas
        if Inscripcion.objects.filter(estudiante=estudiante, materia=materia).exists():
            raise BusinessRuleValidationException(
                f"El estudiante '{estudiante.nombre}' ya se encuentra inscrito en la materia '{materia.nombre}'."
            )

        # 4. Registrar inscripción
        inscripcion = Inscripcion.objects.create(
            estudiante=estudiante,
            materia=materia
        )

        # 5. Auditoría si hay usuario en contexto
        if user and user.is_authenticated:
            Auditoria.objects.create(
                usuario=user,
                accion=AUDIT_ACTION_ENROLL_COURSE,
                tabla=TABLE_INSCRIPCIONES,
                registro_id=inscripcion.id,
                detalles=f"Inscripción de estudiante {estudiante.registro} en materia {materia.codigo}."
            )

        return inscripcion

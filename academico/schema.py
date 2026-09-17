import graphene
from graphene_django import DjangoObjectType
from graphql_jwt.decorators import login_required

from .models import (
    Rol, Usuario, Auditoria, Facultad, Carrera,
    Materia, Estudiante, Docente, EstadoProyecto,
    Proyecto, ProyectoMiembro, Inscripcion
)
from .exceptions import AcademicoDomainException
from .services import ProyectoService, InscripcionService
from . import selectors


# ---------------------------------------------------------------------------
# Tipos GraphQL (DjangoObjectType)
# ---------------------------------------------------------------------------

class RolType(DjangoObjectType):
    class Meta:
        model = Rol
        fields = ('id', 'nombre', 'descripcion')


class UsuarioType(DjangoObjectType):
    ultimo_login = graphene.DateTime()

    class Meta:
        model = Usuario
        fields = (
            'id', 'username', 'email', 'rol', 'activo',
            'ultimo_login', 'created_at', 'updated_at'
        )

    def resolve_ultimo_login(self, info):
        return self.last_login


class AuditoriaType(DjangoObjectType):
    class Meta:
        model = Auditoria
        fields = '__all__'


class FacultadType(DjangoObjectType):
    class Meta:
        model = Facultad
        fields = ('id', 'nombre', 'carreras', 'created_at', 'updated_at')


class CarreraType(DjangoObjectType):
    class Meta:
        model = Carrera
        fields = ('id', 'codigo', 'nombre', 'facultad', 'institucion', 'materias', 'estudiantes')


class MateriaType(DjangoObjectType):
    class Meta:
        model = Materia
        fields = ('id', 'carrera', 'codigo', 'nombre', 'creditos', 'semestre_materia')


class InscripcionType(DjangoObjectType):
    class Meta:
        model = Inscripcion
        fields = ('id', 'estudiante', 'materia', 'fecha_inscripcion')


class DocenteType(DjangoObjectType):
    class Meta:
        model = Docente
        fields = ('id', 'usuario', 'nombre', 'especialidad', 'facultad', 'proyectos_tutorizados')


class EstadoProyectoType(DjangoObjectType):
    class Meta:
        model = EstadoProyecto
        fields = ('id', 'nombre')


class ProyectoMiembroType(DjangoObjectType):
    class Meta:
        model = ProyectoMiembro
        fields = ('id', 'proyecto', 'estudiante', 'rol', 'es_lider')


class ProyectoType(DjangoObjectType):
    class Meta:
        model = Proyecto
        fields = (
            'id', 'estudiante', 'tutor', 'titulo', 'descripcion',
            'estado', 'fecha_inicio', 'fecha_fin', 'created_at',
            'updated_at', 'miembros'
        )


class EstudianteType(DjangoObjectType):
    materias_inscritas = graphene.List(MateriaType)
    proyectos_totales = graphene.List(ProyectoType)

    class Meta:
        model = Estudiante
        fields = (
            'id', 'usuario', 'nombre', 'registro', 'carrera',
            'semestre', 'fecha_nacimiento', 'ppa', 'created_at',
            'updated_at', 'inscripciones', 'proyectos_creados',
            'participaciones_proyectos'
        )

    def resolve_materias_inscritas(self, info):
        return selectors.get_materias_por_estudiante(self)

    def resolve_proyectos_totales(self, info):
        creados = list(self.proyectos_creados.all())
        como_miembro = [m.proyecto for m in self.participaciones_proyectos.select_related('proyecto').all()]
        vistos = set()
        resultado = []
        for p in creados + como_miembro:
            if p.id not in vistos:
                vistos.add(p.id)
                resultado.append(p)
        return resultado


# ---------------------------------------------------------------------------
# Queries delegadas a la capa de Selectores
# ---------------------------------------------------------------------------

class DashboardResumenType(graphene.ObjectType):
    total_estudiantes = graphene.Int()
    total_docentes = graphene.Int()
    total_proyectos = graphene.Int()
    total_materias = graphene.Int()
    promedio_ppa_estudiantes = graphene.Float()


class Query(graphene.ObjectType):
    me = graphene.Field(UsuarioType)
    dashboard_resumen = graphene.Field(DashboardResumenType)

    roles = graphene.List(RolType)
    facultades = graphene.List(FacultadType)
    carreras = graphene.List(CarreraType, facultad_id=graphene.Int(required=False))
    materias = graphene.List(
        MateriaType,
        carrera_id=graphene.Int(required=False),
        semestre=graphene.Int(required=False)
    )
    materia = graphene.Field(MateriaType, id=graphene.Int(required=True))

    docentes = graphene.List(DocenteType)
    docente = graphene.Field(DocenteType, id=graphene.Int(required=True))
    estados_proyecto = graphene.List(EstadoProyectoType)

    proyectos = graphene.List(
        ProyectoType,
        estado_id=graphene.Int(required=False),
        tutor_id=graphene.Int(required=False),
        estudiante_id=graphene.Int(required=False),
        busqueda=graphene.String(required=False)
    )
    proyecto = graphene.Field(ProyectoType, id=graphene.Int(required=True))

    estudiantes = graphene.List(
        EstudianteType,
        carrera_id=graphene.Int(required=False),
        semestre=graphene.Int(required=False)
    )
    estudiante = graphene.Field(
        EstudianteType,
        id=graphene.Int(required=False),
        registro=graphene.String(required=False)
    )

    inscripciones = graphene.List(
        InscripcionType,
        estudiante_id=graphene.Int(required=False),
        materia_id=graphene.Int(required=False)
    )

    auditorias = graphene.List(
        AuditoriaType,
        usuario_id=graphene.Int(required=False),
        tabla=graphene.String(required=False),
        accion=graphene.String(required=False),
        limit=graphene.Int(required=False, default_value=50)
    )

    def resolve_me(self, info):
        user = info.context.user
        return user if user and user.is_authenticated else None

    def resolve_dashboard_resumen(self, info):
        return selectors.get_dashboard_resumen()

    def resolve_roles(self, info):
        return selectors.get_all_roles()

    def resolve_facultades(self, info):
        return selectors.get_all_facultades()

    def resolve_carreras(self, info, facultad_id=None):
        return selectors.get_carreras(facultad_id=facultad_id)

    def resolve_materias(self, info, carrera_id=None, semestre=None):
        return selectors.get_materias(carrera_id=carrera_id, semestre=semestre)

    def resolve_docentes(self, info):
        return selectors.get_docentes()

    def resolve_estados_proyecto(self, info):
        return selectors.get_estados_proyecto()

    def resolve_proyectos(self, info, estado_id=None, tutor_id=None, estudiante_id=None, busqueda=None):
        return selectors.get_proyectos(
            estado_id=estado_id,
            tutor_id=tutor_id,
            estudiante_id=estudiante_id,
            search_query=busqueda
        )

    def resolve_proyecto(self, info, id):
        return selectors.get_proyecto_by_id(proyecto_id=id)

    def resolve_estudiantes(self, info, carrera_id=None, semestre=None):
        return selectors.get_estudiantes(carrera_id=carrera_id, semestre=semestre)

    def resolve_estudiante(self, info, id=None, registro=None):
        if id:
            return selectors.get_estudiante_by_id(estudiante_id=id)
        if registro:
            return selectors.get_estudiante_by_registro(registro=registro)
        return None

    def resolve_materia(self, info, id):
        return selectors.get_materia_by_id(materia_id=id)

    def resolve_docente(self, info, id):
        return selectors.get_docente_by_id(docente_id=id)

    def resolve_inscripciones(self, info, estudiante_id=None, materia_id=None):
        return selectors.get_inscripciones(estudiante_id=estudiante_id, materia_id=materia_id)

    def resolve_auditorias(self, info, usuario_id=None, tabla=None, accion=None, limit=50):
        return selectors.get_auditorias(usuario_id=usuario_id, tabla=tabla, accion=accion, limit=limit)


# ---------------------------------------------------------------------------
# Mutaciones delegadas a la capa de Servicios
# ---------------------------------------------------------------------------

class CrearProyectoInput(graphene.InputObjectType):
    titulo = graphene.String(required=True)
    descripcion = graphene.String(required=False)
    tutor_id = graphene.Int(required=True)
    estudiante_id = graphene.Int(required=False)
    estado_id = graphene.Int(required=False)
    fecha_inicio = graphene.Date(required=False)
    fecha_fin = graphene.Date(required=False)


class CrearProyecto(graphene.Mutation):
    class Arguments:
        input = CrearProyectoInput(required=True)

    proyecto = graphene.Field(ProyectoType)
    ok = graphene.Boolean()
    mensaje = graphene.String()

    @classmethod
    @login_required
    def mutate(cls, root, info, input):
        try:
            proyecto = ProyectoService.crear_proyecto(
                user=info.context.user,
                titulo=input.titulo,
                tutor_id=input.tutor_id,
                descripcion=input.descripcion,
                estudiante_id=input.estudiante_id,
                estado_id=input.estado_id,
                fecha_inicio=input.fecha_inicio,
                fecha_fin=input.fecha_fin
            )
            return CrearProyecto(proyecto=proyecto, ok=True, mensaje="Proyecto creado con éxito.")
        except AcademicoDomainException as exc:
            return CrearProyecto(proyecto=None, ok=False, mensaje=exc.message)
        except Exception as exc:
            return CrearProyecto(proyecto=None, ok=False, mensaje=f"Error inesperado: {str(exc)}")


class InscribirMateriaInput(graphene.InputObjectType):
    estudiante_id = graphene.Int(required=True)
    materia_id = graphene.Int(required=True)


class InscribirMateria(graphene.Mutation):
    class Arguments:
        input = InscribirMateriaInput(required=True)

    inscripcion = graphene.Field(InscripcionType)
    ok = graphene.Boolean()
    mensaje = graphene.String()

    @classmethod
    def mutate(cls, root, info, input):
        try:
            user = info.context.user if hasattr(info.context, 'user') else None
            inscripcion = InscripcionService.inscribir_materia(
                estudiante_id=input.estudiante_id,
                materia_id=input.materia_id,
                user=user
            )
            return InscribirMateria(
                inscripcion=inscripcion,
                ok=True,
                mensaje=f"Estudiante inscrito satisfactoriamente en {inscripcion.materia.nombre}."
            )
        except AcademicoDomainException as exc:
            return InscribirMateria(inscripcion=None, ok=False, mensaje=exc.message)
        except Exception as exc:
            return InscribirMateria(inscripcion=None, ok=False, mensaje=f"Error inesperado: {str(exc)}")


class Mutation(graphene.ObjectType):
    crear_proyecto = CrearProyecto.Field()
    inscribir_materia = InscribirMateria.Field()

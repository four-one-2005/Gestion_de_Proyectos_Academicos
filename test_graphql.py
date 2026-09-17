import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from config.schema import schema
from academico.models import Usuario

def test_queries_and_auth():
    print("--- 1. Probando Query de Catálogos y Proyectos ---")
    query_proyectos = """
    query {
      proyectos {
        id
        titulo
        estado { nombre }
        tutor { nombre }
        estudiante { nombre registro }
        miembros { rol esLider estudiante { nombre } }
      }
    }
    """
    res = schema.execute(query_proyectos)
    print("Resultado proyectos:", res.data)
    assert not res.errors, f"Errores en query proyectos: {res.errors}"

    print("\n--- 2. Probando Query Detallada de Estudiante (Materias y Proyectos) ---")
    query_estudiante = """
    query {
      estudiante(registro: "20241001") {
        nombre
        registro
        carrera { nombre }
        materiasInscritas { codigo nombre creditos }
        proyectosTotales { id titulo }
      }
    }
    """
    res = schema.execute(query_estudiante)
    print("Resultado estudiante:", res.data)
    assert not res.errors, f"Errores en query estudiante: {res.errors}"

    print("\n--- 3. Probando Mutación JWT (tokenAuth) ---")
    mutation_auth = """
    mutation Login($username: String!, $password: String!) {
      tokenAuth(username: $username, password: $password) {
        token
        payload
      }
    }
    """
    from django.test import RequestFactory
    factory = RequestFactory()
    auth_request = factory.post('/graphql')

    res = schema.execute(
        mutation_auth,
        context_value=auth_request,
        variable_values={'username': 'estudiante_perez', 'password': 'password123'}
    )
    print("Resultado JWT:", res.data)
    assert not res.errors, f"Errores en tokenAuth: {res.errors}"
    token = res.data['tokenAuth']['token']
    assert token is not None, "El token JWT no debe ser nulo"

    print("\n--- 4. Probando Mutación Inscribir Materia ---")
    from academico.models import Estudiante, Materia, Inscripcion
    est = Estudiante.objects.first()
    mat = Materia.objects.filter(codigo='INF-312').first()
    # Eliminar inscripción previa si existiera para garantizar prueba idempotente
    Inscripcion.objects.filter(estudiante=est, materia=mat).delete()

    mutation_inscribir = """
    mutation Inscribir($input: InscribirMateriaInput!) {
      inscribirMateria(input: $input) {
        ok
        mensaje
        inscripcion {
          id
          estudiante { nombre }
          materia { codigo nombre }
        }
      }
    }
    """
    res = schema.execute(
        mutation_inscribir,
        variable_values={'input': {'estudianteId': est.id, 'materiaId': mat.id}}
    )
    print("Resultado Inscripción:", res.data)
    assert not res.errors, f"Errores en inscribirMateria: {res.errors}"
    assert res.data['inscribirMateria']['ok'] is True

    # Probar que la regla de negocio bloquea la duplicación (Clean Code business rule)
    res_duplicado = schema.execute(
        mutation_inscribir,
        variable_values={'input': {'estudianteId': est.id, 'materiaId': mat.id}}
    )
    print("Resultado Bloqueo Duplicado:", res_duplicado.data)
    assert res_duplicado.data['inscribirMateria']['ok'] is False
    assert "ya se encuentra inscrito" in res_duplicado.data['inscribirMateria']['mensaje']

    print("\n--- 5. Probando Mutación Crear Proyecto con Usuario Autenticado ---")
    user = Usuario.objects.get(username='estudiante_perez')
    from django.test import RequestFactory
    factory = RequestFactory()
    request = factory.post('/graphql')
    request.user = user

    mutation_proyecto = """
    mutation Nuevo($input: CrearProyectoInput!) {
      crearProyecto(input: $input) {
        ok
        mensaje
        proyecto {
          id
          titulo
          tutor { nombre }
          estado { nombre }
          miembros { rol esLider }
        }
      }
    }
    """
    from academico.models import Docente
    tutor = Docente.objects.first()
    res = schema.execute(
        mutation_proyecto,
        context_value=request,
        variable_values={
            'input': {
                'titulo': 'Plataforma IoT para Sensores Ambientales',
                'tutorId': tutor.id,
                'descripcion': 'Proyecto creado con Clean Architecture y GraphQL'
            }
        }
    )
    print("Resultado Crear Proyecto:", res.data)
    assert not res.errors, f"Errores en crearProyecto: {res.errors}"
    assert res.data['crearProyecto']['ok'] is True

    print("\n¡TODAS LAS PRUEBAS DE INTEGRACIÓN Y CLEAN CODE HAN PASADO EXITOSAMENTE!")

if __name__ == '__main__':
    test_queries_and_auth()

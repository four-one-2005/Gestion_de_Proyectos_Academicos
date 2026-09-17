# Backend API Django + GraphQL (Graphene) + MySQL + JWT

Arquitectura backend desacoplada en Django conectada a una base de datos MySQL preexistente (`academico`).

## Características
- **Modelos sin migraciones destructivas**: Todas las entidades cuentan con `managed = False` y `db_table = '<NombreTabla>'` mapeando las 12 tablas preexistentes.
- **Autenticación desacoplada con JWT**: El modelo de usuario de Django (`AUTH_USER_MODEL`) mapea directamente a la tabla existente `Usuarios` sin crear tablas adicionales.
- **GraphQL con Graphene**:
  - Endpoint único: `/graphql` (con explorador GraphiQL interactivo).
  - Mutaciones JWT: `tokenAuth`, `verifyToken`, `refreshToken`.
  - Mutación protegida `@login_required`: `crearProyecto`.
  - Mutación transaccional: `inscribirMateria`.
  - Consultas con filtrado avanzado y resolución de relaciones anidadas (estudiantes con materias inscritas y proyectos).

---

## Instalación y Configuración

1. **Crear entorno virtual e instalar dependencias**:
   ```bash
   python -m venv venv
   # En Windows:
   venv\Scripts\activate
   # En Linux/Mac:
   source venv/bin/activate

   pip install -r requirements.txt
   ```

2. **Configurar variables de entorno**:
   Copia el archivo `.env.example` como `.env` y ajusta las credenciales de tu MySQL:
   ```bash
   cp .env.example .env
   ```

3. **Ejecutar servidor**:
   ```bash
   python manage.py runserver
   ```
   Accede a la interfaz interactiva de GraphiQL en: `http://127.0.0.1:8000/graphql`

---

## Ejemplos de Consultas GraphQL

### 1. Obtener Token JWT (`tokenAuth`)
```graphql
mutation Login($username: String!, $password: String!) {
  tokenAuth(username: $username, password: $password) {
    token
    payload
    refreshExpiresIn
  }
}
```
*Variables:*
```json
{
  "username": "usuario_ejemplo",
  "password": "tu_password"
}
```

*Para usar en consultas protegidas, envía el header HTTP:*
```text
Authorization: JWT <tu_token_aqui>
```

---

### 2. Verificar Token (`verifyToken`)
```graphql
mutation Verificar($token: String!) {
  verifyToken(token: $token) {
    payload
  }
}
```

---

### 3. Listado y Filtrado de Proyectos
```graphql
query ObtenerProyectos {
  proyectos(busqueda: "Sistema", estadoId: 1) {
    id
    titulo
    descripcion
    fechaInicio
    estado {
      id
      nombre
    }
    tutor {
      id
      nombre
      especialidad
    }
    estudiante {
      id
      nombre
      registro
    }
    miembros {
      id
      rol
      esLider
      estudiante {
        nombre
        registro
      }
    }
  }
}
```

---

### 4. Consulta Detallada de Estudiantes (con Materias Inscritas y Proyectos)
```graphql
query ConsultaEstudiante {
  estudiante(registro: "20241001") {
    id
    nombre
    registro
    semestre
    ppa
    carrera {
      codigo
      nombre
      facultad {
        nombre
      }
    }
    materiasInscritas {
      id
      codigo
      nombre
      creditos
      semestreMateria
    }
    proyectosTotales {
      id
      titulo
      estado {
        nombre
      }
      tutor {
        nombre
      }
    }
  }
}
```

---

### 5. Resumen General del Dashboard (`dashboardResumen`)
```graphql
query ResumenDashboard {
  dashboardResumen {
    totalEstudiantes
    totalDocentes
    totalProyectos
    totalMaterias
    promedioPpaEstudiantes
  }
}
```

---

### 6. Consulta de Inscripciones con Filtros
```graphql
query ListadoInscripciones {
  inscripciones(estudianteId: 1) {
    id
    fechaInscripcion
    estudiante {
      nombre
      registro
    }
    materia {
      codigo
      nombre
      creditos
    }
  }
}
```

---

### 7. Consulta de Registro de Auditoría
```graphql
query HistorialAuditoria {
  auditorias(tabla: "Proyectos", limit: 10) {
    id
    accion
    tabla
    registroId
    detalles
    fecha
    usuario {
      username
    }
  }
}
```

---

### 8. Consulta de Docente Detallado con Proyectos Tutorizados
```graphql
query DetalleDocente {
  docente(id: 1) {
    id
    nombre
    especialidad
    facultad
    proyectosTutorizados {
      id
      titulo
      estado {
        nombre
      }
    }
  }
}
```

---

### 5. Mutación Protegida: Crear Proyecto (`@login_required`)
*(Requiere header `Authorization: JWT <token>`)*
```graphql
mutation NuevoProyecto($input: CrearProyectoInput!) {
  crearProyecto(input: $input) {
    ok
    mensaje
    proyecto {
      id
      titulo
      fechaInicio
      estado {
        nombre
      }
      tutor {
        nombre
      }
      estudiante {
        nombre
      }
      miembros {
        rol
        esLider
        estudiante {
          nombre
        }
      }
    }
  }
}
```
*Variables:*
```json
{
  "input": {
    "titulo": "Implementación de Red Neuronal para Predicción Académica",
    "descripcion": "Proyecto de grado enfocado en optimización de rendimiento estudiantil.",
    "tutorId": 1
  }
}
```

---

### 6. Mutación: Inscribir Estudiante a Materia
```graphql
mutation Inscribir($input: InscribirMateriaInput!) {
  inscribirMateria(input: $input) {
    ok
    mensaje
    inscripcion {
      id
      fechaInscripcion
      estudiante {
        nombre
        registro
      }
      materia {
        codigo
        nombre
      }
    }
  }
}
```
*Variables:*
```json
{
  "input": {
    "estudianteId": 1,
    "materiaId": 2
  }
}
```

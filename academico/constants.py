"""
Constantes de dominio para la aplicación académica.
Centraliza identificadores, cadenas y nombres mágicos para Clean Code.
"""

from typing import Final

# Roles del sistema
ROLE_ADMIN: Final[str] = "ADMIN"
ROLE_ADMINISTRADOR: Final[str] = "ADMINISTRADOR"
ROLE_DOCENTE: Final[str] = "DOCENTE"
ROLE_ESTUDIANTE: Final[str] = "ESTUDIANTE"

ADMIN_ROLES: Final[tuple[str, ...]] = (ROLE_ADMIN, ROLE_ADMINISTRADOR)

# Acciones de Auditoría
AUDIT_ACTION_LOGIN: Final[str] = "LOGIN"
AUDIT_ACTION_CREATE_PROJECT: Final[str] = "CREAR_PROYECTO"
AUDIT_ACTION_UPDATE_PROJECT: Final[str] = "ACTUALIZAR_PROYECTO"
AUDIT_ACTION_ENROLL_COURSE: Final[str] = "INSCRIBIR_MATERIA"

# Nombres de Tablas para Auditoría
TABLE_PROYECTOS: Final[str] = "Proyectos"
TABLE_INSCRIPCIONES: Final[str] = "Inscripciones"
TABLE_USUARIOS: Final[str] = "Usuarios"

# Roles de miembro en proyectos
PROJECT_ROLE_LEADER: Final[str] = "Líder de Proyecto"
PROJECT_ROLE_COLLABORATOR: Final[str] = "Colaborador"

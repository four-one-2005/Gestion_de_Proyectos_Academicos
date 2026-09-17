"""
Excepciones de dominio personalizadas para la capa de servicios.
Evita el acoplamiento directo de errores HTTP o de base de datos en la lógica de negocio.
"""


class AcademicoDomainException(Exception):
    """Excepción base para el dominio académico."""
    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class ResourceNotFoundException(AcademicoDomainException):
    """Lanzada cuando una entidad requerida no existe en la base de datos."""
    pass


class BusinessRuleValidationException(AcademicoDomainException):
    """Lanzada cuando una regla de negocio o restricción es infringida."""
    pass


class UnauthorizedActionException(AcademicoDomainException):
    """Lanzada cuando un usuario no tiene permisos suficientes para la acción."""
    pass

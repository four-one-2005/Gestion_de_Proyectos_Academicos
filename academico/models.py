from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


class Rol(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'Roles'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class UsuarioManager(BaseUserManager):
    def create_user(self, username, email=None, password=None, **extra_fields):
        if not username:
            raise ValueError('El campo username es obligatorio.')
        email = self.normalize_email(email) if email else None
        user = self.model(username=username, email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('activo', True)
        return self.create_user(username, email, password, **extra_fields)


class Usuario(AbstractBaseUser, PermissionsMixin):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True, blank=True, null=True)
    rol = models.ForeignKey(Rol, models.DO_NOTHING, db_column='rol_id')
    activo = models.BooleanField(default=True)
    last_login = models.DateTimeField(db_column='ultimo_login', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(blank=True, null=True)

    # Required fields for Django auth
    groups = None
    user_permissions = None

    objects = UsuarioManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    @property
    def ultimo_login(self):
        return self.last_login

    @ultimo_login.setter
    def ultimo_login(self, value):
        self.last_login = value

    class Meta:
        managed = False
        db_table = 'Usuarios'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    @property
    def is_active(self):
        return bool(self.activo and self.deleted_at is None)

    @property
    def is_staff(self):
        # Allow staff access if rol is Administrador or similar
        return bool(self.rol and self.rol.nombre.lower() in ['admin', 'administrador'])

    @property
    def is_superuser(self):
        return self.is_staff

    def has_perm(self, perm, obj=None):
        return self.is_active

    def has_module_perms(self, app_label):
        return self.is_active

    def __str__(self):
        return self.username


class Auditoria(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.ForeignKey(Usuario, models.DO_NOTHING, db_column='usuario_id')
    accion = models.CharField(max_length=50)
    tabla = models.CharField(max_length=100)
    registro_id = models.PositiveIntegerField()
    detalles = models.TextField(blank=True, null=True)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Auditoria'
        verbose_name = 'Auditoría'
        verbose_name_plural = 'Auditorías'

    def __str__(self):
        return f"{self.accion} en {self.tabla} (#{self.registro_id}) por {self.usuario.username}"


class Facultad(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'Facultades'
        verbose_name = 'Facultad'
        verbose_name_plural = 'Facultades'

    def __str__(self):
        return self.nombre


class Carrera(models.Model):
    id = models.AutoField(primary_key=True)
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    facultad = models.ForeignKey(Facultad, models.DO_NOTHING, db_column='facultad_id', related_name='carreras')
    institucion = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'Carreras'
        verbose_name = 'Carrera'
        verbose_name_plural = 'Carreras'

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Materia(models.Model):
    id = models.AutoField(primary_key=True)
    carrera = models.ForeignKey(Carrera, models.DO_NOTHING, db_column='carrera_id', related_name='materias')
    codigo = models.CharField(max_length=20)
    nombre = models.CharField(max_length=150)
    creditos = models.PositiveIntegerField()
    semestre_materia = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'Materias'
        verbose_name = 'Materia'
        verbose_name_plural = 'Materias'
        unique_together = (('carrera', 'codigo'),)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


class Estudiante(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, models.DO_NOTHING, db_column='usuario_id', related_name='estudiante_perfil')
    nombre = models.CharField(max_length=150)
    registro = models.CharField(max_length=50, unique=True)
    carrera = models.ForeignKey(Carrera, models.DO_NOTHING, db_column='carrera_id', related_name='estudiantes')
    semestre = models.PositiveSmallIntegerField()
    fecha_nacimiento = models.DateField(blank=True, null=True)
    ppa = models.DecimalField(max_digits=3, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'Estudiantes'
        verbose_name = 'Estudiante'
        verbose_name_plural = 'Estudiantes'

    def __str__(self):
        return f"{self.registro} - {self.nombre}"


class Docente(models.Model):
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(Usuario, models.DO_NOTHING, db_column='usuario_id', related_name='docente_perfil')
    nombre = models.CharField(max_length=150)
    especialidad = models.CharField(max_length=150, blank=True, null=True)
    facultad = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'Docentes'
        verbose_name = 'Docente'
        verbose_name_plural = 'Docentes'

    def __str__(self):
        return self.nombre


class EstadoProyecto(models.Model):
    id = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)

    class Meta:
        managed = False
        db_table = 'EstadoProyecto'
        verbose_name = 'Estado de Proyecto'
        verbose_name_plural = 'Estados de Proyecto'

    def __str__(self):
        return self.nombre


class Proyecto(models.Model):
    id = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='estudiante_id', related_name='proyectos_creados')
    tutor = models.ForeignKey(Docente, models.DO_NOTHING, db_column='tutor_id', related_name='proyectos_tutorizados')
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    estado = models.ForeignKey(EstadoProyecto, models.DO_NOTHING, db_column='estado_id', related_name='proyectos')
    fecha_inicio = models.DateField(blank=True, null=True)
    fecha_fin = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        managed = False
        db_table = 'Proyectos'
        verbose_name = 'Proyecto'
        verbose_name_plural = 'Proyectos'

    def __str__(self):
        return self.titulo


class ProyectoMiembro(models.Model):
    id = models.AutoField(primary_key=True)
    proyecto = models.ForeignKey(Proyecto, models.DO_NOTHING, db_column='proyecto_id', related_name='miembros')
    estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='estudiante_id', related_name='participaciones_proyectos')
    rol = models.CharField(max_length=50, blank=True, null=True)
    es_lider = models.BooleanField(default=False)

    class Meta:
        managed = False
        db_table = 'ProyectosMiembros'
        verbose_name = 'Miembro de Proyecto'
        verbose_name_plural = 'Miembros de Proyectos'
        unique_together = (('proyecto', 'estudiante'),)

    def __str__(self):
        return f"{self.estudiante.nombre} en {self.proyecto.titulo}"


class Inscripcion(models.Model):
    id = models.AutoField(primary_key=True)
    estudiante = models.ForeignKey(Estudiante, models.DO_NOTHING, db_column='estudiante_id', related_name='inscripciones')
    materia = models.ForeignKey(Materia, models.DO_NOTHING, db_column='materia_id', related_name='inscripciones')
    fecha_inscripcion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = False
        db_table = 'Inscripciones'
        verbose_name = 'Inscripción'
        verbose_name_plural = 'Inscripciones'
        unique_together = (('estudiante', 'materia'),)

    def __str__(self):
        return f"{self.estudiante.registro} -> {self.materia.codigo}"

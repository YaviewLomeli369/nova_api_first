from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group, Permission
from accounts.models import Usuario, Rol, Auditoria

# 🔐 Usuario Admin
@admin.register(Usuario)
class UsuarioAdmin(BaseUserAdmin):
    list_display = ('username', 'email', 'empresa', 'rol', 'is_active', 'last_login')
    list_filter = ('rol', 'empresa', 'is_active', 'is_superuser')
    search_fields = ('username', 'email', 'rol__nombre', 'empresa__nombre')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Información Personal', {'fields': ('email', 'empresa', 'rol')}),
        ('Permisos del Sistema', {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Accesos y Registro', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'empresa', 'rol', 'password1', 'password2',
                       'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
    )

# 🔧 Rol Admin
@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)
    ordering = ('nombre',)

# 🕵️ Auditoría Admin (Solo lectura)
@admin.register(Auditoria)
class AuditoriaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp')
    list_filter = ('accion', 'tabla_afectada', 'timestamp')
    search_fields = ('usuario__username', 'accion', 'tabla_afectada', 'registro_afectado')
    readonly_fields = ('usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

# ✅ Permitir gestionar permisos y grupos desde el admin
admin.site.unregister(Group)
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    filter_horizontal = ('permissions',)

@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'codename', 'content_type')
    list_filter = ('content_type',)
    search_fields = ('name', 'codename')


# # accounts/admin.py
# from django.contrib import admin
# from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
# from accounts.models import Usuario, Rol, Auditoria

# @admin.register(Usuario)
# class UsuarioAdmin(BaseUserAdmin):
#     list_display = ('username', 'email', 'empresa', 'rol')  # elimina is_staff, is_active
#     list_filter = ('rol', 'empresa')  # elimina is_staff, is_active

#     # Campos para el formulario de edición
#     fieldsets = (
#         (None, {'fields': ('username', 'password')}),
#         ('Información Personal', {'fields': ('email', 'empresa', 'rol')}),
#         ('Permisos', {'fields': ('is_staff', 'is_active', 'is_superuser', 'groups', 'user_permissions')}),
#         ('Fechas importantes', {'fields': ('last_login', 'date_joined')}),
#     )

#     # Campos que se usarán para crear usuario
#     add_fieldsets = (
#         (None, {
#             'classes': ('wide',),
#             'fields': ('username', 'email', 'empresa', 'rol', 'password1', 'password2', 'is_staff', 'is_active')}
#         ),
#     )

#     search_fields = ('username', 'email')
#     ordering = ('username',)

# @admin.register(Rol)
# class RolAdmin(admin.ModelAdmin):
#     list_display = ('nombre', 'descripcion')
#     list_display = ('nombre', 'descripcion')


# @admin.register(Auditoria)
# class AuditoriaAdmin(admin.ModelAdmin):
#     list_display = ('usuario', 'accion', 'tabla_afectada', 'timestamp')
#     list_filter = ('accion', 'tabla_afectada', 'timestamp')
#     search_fields = ('usuario__username', 'accion', 'tabla_afectada', 'registro_afectado')
#     readonly_fields = ('usuario', 'accion', 'tabla_afectada', 'registro_afectado', 'timestamp')

#     def has_add_permission(self, request):
#         return False  # No se permite agregar registros manualmente

#     def has_delete_permission(self, request, obj=None):
#         return False  # Opcional: impedir borrar registros para mantener integridad
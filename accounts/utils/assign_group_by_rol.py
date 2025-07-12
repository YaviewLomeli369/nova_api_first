from django.contrib.auth.models import Group

def assign_group_by_rol(user):
    if user.rol:
        group, _ = Group.objects.get_or_create(name=user.rol.nombre)
        user.groups.set([group])

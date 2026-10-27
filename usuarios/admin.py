
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("id", "username", "email", "rol", "is_active", "is_staff")
    list_filter = ("rol", "is_active", "is_staff")
    search_fields = ("username", "email")

    fieldsets = UserAdmin.fieldsets + (
        ("Información de Coramanda", {"fields": ("rol",)}),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Información de Coramanda", {"fields": ("email", "rol")}),
    )

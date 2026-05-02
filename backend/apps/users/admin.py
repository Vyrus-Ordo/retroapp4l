from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	ordering = ("email",)
	list_display = ("email", "name", "oauth_provider", "is_active", "created_at")
	fieldsets = (
		(None, {"fields": ("email", "password")}),
		("Profile", {"fields": ("name", "avatar_url", "oauth_provider", "oauth_id")}),
		("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
		("Dates", {"fields": ("last_login", "created_at")}),
	)
	add_fieldsets = (
		(
			None,
			{
				"classes": ("wide",),
				"fields": ("email", "name", "password1", "password2", "is_active", "is_staff"),
			},
		),
	)
	readonly_fields = ("created_at", "last_login")
	search_fields = ("email", "name")

# Register your models here.

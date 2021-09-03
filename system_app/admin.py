from django.contrib import admin
from django.contrib.auth.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email")
    list_filter = ("is_staff", "is_superuser")
    fields = ("email", "first_name", "last_name", "groups", "user_permissions")

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, change, **kwargs)
        form.base_fields["email"].required = True
        form.base_fields["first_name"].required = True
        form.base_fields["last_name"].required = True
        return form

    def save_form(self, request, form, change):
        user = super().save_form(request, form, change)
        user.username = user.email
        user.set_unusable_password()
        return user


admin.site.unregister(User)
admin.site.register(User, UserAdmin)


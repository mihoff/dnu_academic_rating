from django.contrib import admin
from django.contrib.auth.models import User

from system_app.models import Documents


class UserAdmin(admin.ModelAdmin):
    list_display = ("last_name", "first_name", "email")
    list_filter = ("is_staff", "is_superuser")
    fields = ("email", "first_name", "last_name", "groups", "user_permissions")
    search_fields = ('first_name', 'last_name', 'email')

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


@admin.register(Documents)
class DocumentsAdmin(admin.ModelAdmin):
    list_display = ("name", "description", "visible")

    def save_model(self, request, obj, form, change):
        if obj.name is None:
            obj.name = obj.file.name.replace(Documents.file.field.upload_to + "/", "").split(".")[0]
        super().save_model(request, obj, form, change)


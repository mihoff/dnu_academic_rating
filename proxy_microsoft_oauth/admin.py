from django.contrib import admin
from microsoft_auth.admin import MicrosoftAccountAdmin
from microsoft_auth.models import MicrosoftAccount


class MicrosoftAccountAdminOverride(MicrosoftAccountAdmin):
    list_display = ["user__first_name", "user__last_name", "user__email"]
    actions = ["view"]

    def has_add_permission(self, request):
        return False

    @admin.display(description='Прізвище')
    def user__first_name(self, obj):
        return obj.user.first_name

    @admin.display(description='Ім\'я по батькові')
    def user__last_name(self, obj):
        return obj.user.last_name

    @admin.display(description='Електронна скриня')
    def user__email(self, obj):
        return obj.user.email


admin.site.unregister(MicrosoftAccount)
admin.site.register(MicrosoftAccount, MicrosoftAccountAdminOverride)

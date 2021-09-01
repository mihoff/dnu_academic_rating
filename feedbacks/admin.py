from django.contrib import admin

from feedbacks.models import Feedback


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "user_", "feedback_", "seen", "comment_", "created_at", "updated_at")

    @admin.display(description="Користувач")
    def user_(self, obj):
        return obj.user.profile.last_name_and_initial if obj.user else ""

    @admin.display(description=Feedback.feedback.field.verbose_name)
    def feedback_(self, obj):
        return f"{obj.feedback[:30]}..." if obj.feedback else ""

    @admin.display(description=Feedback.comment.field.verbose_name)
    def comment_(self, obj):
        return f"{obj.comment[:30]}..." if obj.comment else ""

from django.forms import ModelForm
from django.http import HttpResponse, Http404
from django.views.decorators.http import require_http_methods

from feedbacks.models import Feedback


class FeedbackForm(ModelForm):
    class Meta:
        model = Feedback
        fields = ["name", "feedback"]


@require_http_methods(["POST"])
def feedbacks(request):
    if not request.is_ajax():
        return Http404

    f = FeedbackForm(request.POST)
    if f.is_valid():
        feedback = f.save(commit=False)
        if request.user.is_authenticated:
            feedback.user = request.user
        feedback.save()
        return HttpResponse("Дякуємо за відгук!")

    return HttpResponse("Під час збережння відгуку виникла помилка, спробуйте, будь-ласка, пізніше.")

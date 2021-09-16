from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.views.generic import ListView

from system_app.models import Documents


class DocumentsView(LoginRequiredMixin, ListView):
    model = Documents
    template_name = "service_app/documents.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data["is_documents"] = True
        return data

    def get(self, request, *args, **kwargs):
        pk = kwargs.get("pk")
        if pk is not None:
            obj = self.model.objects.get(pk=pk)
            filename = f"{obj.name}.{obj.file.name.split('.')[-1]}"
            response = HttpResponse(obj.file.read(), content_type="application/octet-stream")
            response["Content-Disposition"] = f"attachment; filename={filename}".encode("utf-8")
            return response
        return super().get(request, *args, **kwargs)

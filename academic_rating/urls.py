"""
    academic_rating URL Configuration
"""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from feedbacks.views import feedbacks
from proxy_microsoft_oauth.views import logout_view, AuthenticateCallbackViewOverwrite
from service_api.views import IndexView, EducationalAndMethodicalWorkView, ScientificAndInnovativeWorkView, \
    GenericReportDataView, ReportsView, OrganizationalAndEducationalWorkView, ReportPdf, \
    pivot_report_by_type
from system_app.views import DocumentsView

urlpatterns = [
    path("", IndexView.as_view(), name="index"),
    path("admin/logout/", logout_view, name="logout_"),
    path("logout/", logout_view, name="logout_"),
    path("admin/", admin.site.urls),
    path("accounts/logout/", logout_view),
    path("accounts/", include("django.contrib.auth.urls")),
    path("microsoft/auth-callback/", AuthenticateCallbackViewOverwrite.as_view(), name="auth-callback"),
    path("microsoft/", include("microsoft_auth.urls", namespace="microsoft")),
    path("fillin/generic-report-data/", GenericReportDataView.as_view(), name="generic_report_data"),
    path("fillin/educational-and-methodical-work/", EducationalAndMethodicalWorkView.as_view(),
         name="educational_and_methodical_work"),
    path("fillin/scientific-and-innovative-work/", ScientificAndInnovativeWorkView.as_view(),
         name="scientific_and_innovative_work"),
    path("fillin/organizational-and-educational-work/", OrganizationalAndEducationalWorkView.as_view(),
         name="organizational_and_educational_work"),
    path("reports/", ReportsView.as_view(), name="reports"),
    path("reports/<str:report_period>/", ReportsView.as_view(), name="reports"),
    path("reports/pdf/<str:report_period>", ReportPdf.as_view(), name="report_pdf"),
    path("pivot-report/<int:report_period_id>", pivot_report_by_type, name="pivot_report_all"),
    path("pivot-report/<int:report_period_id>/<str:level_type>/<int:pk>", pivot_report_by_type,
         name="pivot_report_by_type"),
    path("documents/", DocumentsView.as_view(), name="documents"),
    path("documents/<int:pk>", DocumentsView.as_view(), name="documents"),

    path("feedbacks/", feedbacks, name="feedbacks")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


admin.site.site_header = "Адміністрування \"Рейтинг Викладача\""

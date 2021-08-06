import codecs
import csv

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.base import ContextMixin
from django_tables2 import LazyPaginator, SingleTableView
from microsoft_auth.context_processors import microsoft

from service_api.calculations import BaseCalculation
from service_api.calculations.educational_and_methodical_work_calc import EducationalAndMethodicalWorkCalculation
from service_api.calculations.generic_report_calc import GenericReportCalculation, HeadsGetter
from service_api.calculations.organizational_and_educational_work_calc import \
    OrganizationalAndEducationalWorkCalculation
from service_api.calculations.scientific_and_innovative_work_calc import ScientificAndInnovativeWorkCalculation
from service_api.forms.report_forms import GenericReportDataForm, EducationalAndMethodicalWorkForm, \
    OrganizationalAndEducationalWorkForm, ScientificAndInnovativeWorkForm
from service_api.models import GenericReportData, EducationalAndMethodicalWork, OrganizationalAndEducationalWork, \
    ScientificAndInnovativeWork, ReportPeriod
from service_api.tables import PivotReportTable
from user_profile.models import Profile, Position, Faculty, Department


class BaseView(ContextMixin, LoginRequiredMixin):
    report_period: ReportPeriod = None
    generic_report: GenericReportData = None

    def dispatch(self, request, *args, **kwargs):
        report_period_str = (kwargs.get("report_period") or "").replace("-", '/')
        if report_period_str:
            self.report_period = ReportPeriod.objects.filter(report_period=report_period_str).first()
        else:
            self.report_period = ReportPeriod.get_active()

        if request.user.is_authenticated:
            self.generic_report = GenericReportData.objects.filter(
                user=request.user, report_period=self.report_period).first()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        extended_user = False
        if self.request.user.is_authenticated \
                and self.request.user.profile.position is not None \
                and self.request.user.profile.position.cumulative_calculation is not None:
            extended_user = True

        if self.generic_report:
            is_editable = not self.generic_report.is_closed
        elif self.report_period:
            is_editable = self.report_period.is_active
        else:
            is_editable = True

        data.update(
            {
                "report_period": self.report_period,
                "generic_report": self.generic_report,
                "extended_user": extended_user,
                "is_editable": is_editable
            }
        )
        return data


class BaseReportFormView(FormView, BaseView):
    model: type(models.Model) = None
    calc_model: type(BaseCalculation) = None
    template_name = "base_report.html"
    report_template_path: str = None

    def get_object(self, report_period: ReportPeriod):
        return self.model.get_report(self.request.user, report_period)

    def get_form(self, form_class=None):
        obj = self.get_object(ReportPeriod.get_active())
        return self.form_class(instance=obj, **self.get_form_kwargs())

    def update_generic_report(self):
        self.__update_generic_report(self.generic_report)

    @staticmethod
    def __update_generic_report(generic_report):
        calc_obj = GenericReportCalculation(generic_report)
        generic_report.result = calc_obj.get_result()
        generic_report.save()

    def update_reports_of_heads(self):
        profile = self.request.user.profile
        heads = HeadsGetter(profile.department, profile.department.faculty)
        if heads.head_of_department_profile is not None and profile != heads.head_of_department_profile:
            generic_report = heads.head_of_department_profile.user.genericreportdata_set.filter(
                report_period=ReportPeriod.get_active()).first()
            self.__update_generic_report(generic_report)
        if heads.head_of_faculty_profile is not None and profile != heads.head_of_faculty_profile:
            generic_report = heads.head_of_faculty_profile.user.genericreportdata_set.filter(
                report_period=ReportPeriod.get_active()).first()
            self.__update_generic_report(generic_report)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "report_name": self.model.NAME,
                f"is_{self.model.slug()}": True,
                "report_template_path": self.report_template_path
            }
        )
        return data

    def form_valid(self, form):
        f = form.save(commit=False)
        active_report_period = ReportPeriod.get_active()
        if not self.get_object(active_report_period):
            f.generic_report_data = GenericReportData.objects.get(
                user=self.request.user, report_period=active_report_period)
        calc_obj = self.calc_model(f)
        f.result = calc_obj.get_result()
        f.adjusted_result = self.model.raw_calculation(f.result, self.generic_report)
        f.save()

        self.update_generic_report()

        self.update_reports_of_heads()

        messages.success(self.request, f'Дані по "{self.model.NAME}" збережено')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Виправте помилки та спробуйте ще раз")
        return super().form_invalid(form)


class IndexView(TemplateView, BaseView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "is_index": True,
                **microsoft(self.request)
            }
        )
        return data


class PivotReportView(BaseView, SingleTableView):
    template_name = "service_api/pivot_report_test.html"
    paginator_class = LazyPaginator
    table_class = PivotReportTable

    def get_queryset(self):
        if self.request.user.profile.position.cumulative_calculation == Position.BY_DEPARTMENT:
            profiles = Profile.objects.filter(department=self.request.user.profile.department)
        elif self.request.user.profile.position.cumulative_calculation == Position.BY_FACULTY:
            profiles = Profile.objects.filter(department__faculty=self.request.user.profile.department.faculty)
        else:
            raise Http404
        return profiles

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data["is_pivot_report"] = True
        return data


class GenericReportDataView(BaseReportFormView):
    """
        Форма загальных даних для звітів
    """
    model = GenericReportData
    form_class = GenericReportDataForm
    report_template_path = "service_api/raw_report_forms/raw_generic_report_data_view.html"
    success_url = reverse_lazy("generic_report_data")
    calc_model = GenericReportCalculation

    def get_object(self, report_period):
        return self.generic_report

    def form_valid(self, form):
        f = form.save(commit=False)
        active_report_period = ReportPeriod.get_active()
        if not self.get_object(active_report_period):
            f.user = self.request.user
            f.report_period = active_report_period
        calc_obj = self.calc_model(f)
        f.result = calc_obj.get_result()
        f.save()

        self.update_reports_of_heads()

        messages.success(self.request, "Загальні дані збережено")
        return HttpResponseRedirect(self.get_success_url())


class EducationalAndMethodicalWorkView(BaseReportFormView):
    """
        1. Навчально-методична робота
    """
    model = EducationalAndMethodicalWork
    form_class = EducationalAndMethodicalWorkForm
    report_template_path = "service_api/raw_report_forms/raw_educational_and_methodical_work.html"
    success_url = reverse_lazy("educational_and_methodical_work")
    calc_model = EducationalAndMethodicalWorkCalculation


class ScientificAndInnovativeWorkView(BaseReportFormView):
    """
        2. Науково-інноваційна робота
    """
    model = ScientificAndInnovativeWork
    form_class = ScientificAndInnovativeWorkForm
    report_template_path = "service_api/raw_report_forms/raw_scientific_and_innovative_work.html"
    success_url = reverse_lazy("scientific_and_innovative_work")
    calc_model = ScientificAndInnovativeWorkCalculation


class OrganizationalAndEducationalWorkView(BaseReportFormView):
    """
        3. Організаційно-виховна робота
    """
    model = OrganizationalAndEducationalWork
    form_class = OrganizationalAndEducationalWorkForm
    report_template_path = "service_api/raw_report_forms/raw_organizational_and_educational_work.html"
    success_url = reverse_lazy("organizational_and_educational_work")
    calc_model = OrganizationalAndEducationalWorkCalculation


class ReportsView(TemplateView, BaseView):
    template_name = "service_api/reports.html"

    def get_context_data(self, report_period: str = None, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "is_report": True,
                "report_periods": GenericReportData.objects.filter(user=self.request.user),
            }
        )
        return data


class ReportPdf(TemplateView, BaseView):
    template_name = "service_api/reports/report.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        report_instances = {}
        for _model, _form in ((EducationalAndMethodicalWork, EducationalAndMethodicalWorkForm),
                              (ScientificAndInnovativeWork, ScientificAndInnovativeWorkForm),
                              (OrganizationalAndEducationalWork, OrganizationalAndEducationalWorkForm)):
            report_instances[_model.slug()] = None
            if hasattr(self.generic_report, _model.__name__.lower()):
                report_instances[_model.slug()] = _form(instance=getattr(self.generic_report, _model.__name__.lower()))

        data.update(
            {
                **report_instances,
                "is_editable": False,
                "is_pdf": True,
                GenericReportData.slug():
                    GenericReportDataForm(instance=self.generic_report) if self.generic_report else None,
                "report_name":
                    f"Рейтингові бали {self.request.user.profile.last_name_and_initial} "
                    f"за {self.report_period} навчальний рік"
            }
        )
        return data


class PivotReport:
    def __init__(self, request, report_period_id=None, level_type=None, pk=None):
        self.request = request
        self.report_period_id = report_period_id
        self.level_type = level_type
        self.pk = pk

        self.__response = None

    def get_qs(self):
        return GenericReportData.objects.filter(report_period__pk=self.report_period_id).order_by("-result")

    def is_valid(self, generic_report: GenericReportData):
        if self.level_type == Faculty.__name__.lower():
            return generic_report.user.profile.department.faculty.pk == self.pk
        elif self.level_type == Department.__name__.lower():
            return generic_report.user.profile.department.pk == self.pk
        else:
            return True

    def prepare_response(self):
        report_period = ReportPeriod.objects.get(pk=self.report_period_id)
        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition":
                    f"attachment; filename=Звітний період {report_period.report_period}.csv".encode("utf-8")
            }
        )
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(["#", "ПІБ", "Кафедра", "Факультет", "Посада", "Підсумковий Бал"])
        for i, one in enumerate(self.get_qs(), start=1):
            if self.is_valid(one):
                writer.writerow(
                    [
                        i,
                        one.user.profile.last_name_and_initial,
                        one.user.profile.department,
                        one.user.profile.department.faculty,
                        one.user.profile.position,
                        one.result,
                    ]
                )

        self.__response = response

    @property
    def response(self):
        return self.__response


def pivot_report_by_type(request, report_period_id, level_type=None, pk=None):
    report = PivotReport(request, report_period_id=report_period_id, level_type=level_type, pk=pk)
    report.prepare_response()
    return report.response

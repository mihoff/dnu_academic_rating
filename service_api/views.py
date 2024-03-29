import codecs
import csv
import logging
import traceback

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import models
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse_lazy
from django.views.generic import TemplateView, FormView
from django.views.generic.base import ContextMixin, View
from microsoft_auth.context_processors import microsoft

from service_api.calculations import BaseCalculation
from service_api.calculations.educational_and_methodical_work_calc import (
    EducationalAndMethodicalWorkCalculation,
)
from service_api.calculations.generic_report_calc import (
    GenericReportCalculation,
    HeadsGetter,
)
from service_api.calculations.organizational_and_educational_work_calc import (
    OrganizationalAndEducationalWorkCalculation,
)
from service_api.calculations.scientific_and_innovative_work_calc import (
    ScientificAndInnovativeWorkCalculation,
)
from service_api.forms.report_forms import (
    GenericReportDataForm,
    EducationalAndMethodicalWorkForm,
    OrganizationalAndEducationalWorkForm,
    ScientificAndInnovativeWorkForm,
)
from service_api.models import (
    GenericReportData,
    EducationalAndMethodicalWork,
    OrganizationalAndEducationalWork,
    ScientificAndInnovativeWork,
    ReportPeriod,
    TeacherResults,
    HeadsOfDepartmentsResults,
    FacultyResults,
    DecansResults,
)
from user_profile.models import Faculty, Department

logger = logging.getLogger()


class __BaseView(ContextMixin):
    report_period: ReportPeriod = None
    generic_report: GenericReportData = None

    def dispatch(self, request, *args, **kwargs):
        report_period_str = (kwargs.get("report_period") or "").replace("-", "/")
        if report_period_str:
            self.report_period = ReportPeriod.objects.filter(report_period=report_period_str).first()
        else:
            self.report_period = ReportPeriod.get_active()

        if request.user.is_authenticated:
            self.generic_report = GenericReportData.objects.filter(
                user=request.user, report_period=self.report_period
            ).first()

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        extended_user = False
        if (
            self.request.user.is_authenticated
            and self.request.user.profile.position is not None
            and self.request.user.profile.position.cumulative_calculation is not None
        ):
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
                "is_editable": is_editable,
            }
        )
        return data


class BaseView(LoginRequiredMixin, __BaseView):
    ...


class BaseReportFormView(BaseView, FormView):
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
        if generic_report:
            calc_obj = GenericReportCalculation(generic_report)
            generic_report.result = calc_obj.get_result()
            generic_report.save()

    def update_reports_of_heads(self):
        profile = self.request.user.profile
        heads = HeadsGetter(profile.department, profile.department.faculty)
        if heads.head_of_department_profile is not None and profile != heads.head_of_department_profile:
            generic_report = heads.head_of_department_profile.user.genericreportdata_set.filter(
                report_period=ReportPeriod.get_active()
            ).first()
            self.__update_generic_report(generic_report)
        if heads.head_of_faculty_profile is not None and profile != heads.head_of_faculty_profile:
            generic_report = heads.head_of_faculty_profile.user.genericreportdata_set.filter(
                report_period=ReportPeriod.get_active()
            ).first()
            self.__update_generic_report(generic_report)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "report_name": self.model.NAME,
                f"is_{self.model.slug()}": True,
                "report_template_path": self.report_template_path,
                "is_pdf": False,
            }
        )
        return data

    def form_valid(self, form):
        f = form.save(commit=False)
        active_report_period = ReportPeriod.get_active()
        if not self.get_object(active_report_period):
            f.generic_report_data = GenericReportData.objects.get(
                user=self.request.user, report_period=active_report_period
            )
        # calc_obj = self.calc_model(f)
        try:
            # f.result = calc_obj.get_result()
            # f.adjusted_result = self.model.raw_calculation(
            #     f.result, self.generic_report
            # )
            f.save()

            # self.update_generic_report()

            # self.update_reports_of_heads()
        except:
            logger.exception(f"{self.request.user}\n{form.data}\n{traceback.format_exc()}")
            return self.form_invalid(form)

        messages.success(self.request, f'Дані по "{self.model.NAME}" збережено')
        return super().form_valid(form)

    def form_invalid(self, form):
        messages.error(self.request, "Виправте помилки та спробуйте ще раз")
        return super().form_invalid(form)


class IndexView(__BaseView, TemplateView):
    template_name = "index.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update({"is_index": True, **microsoft(self.request)})
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
        # calc_obj = self.calc_model(f)
        # f.result = calc_obj.get_result()
        f.save()

        # self.update_reports_of_heads()

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


class ReportsView(BaseView, TemplateView):
    template_name = "service_api/reports.html"

    def get_context_data(self, report_period: str = None, **kwargs):
        data = super().get_context_data(**kwargs)
        data.update(
            {
                "is_pdf": False,
                "is_report": True,
                "user_reports": GenericReportData.objects.filter(user=self.request.user),
                "teacher_result": TeacherResults.objects.filter(
                    generic_report_data__user=self.request.user,
                    generic_report_data__report_period=data["report_period"],
                ).first(),
            }
        )
        return data


class ReportPdf(BaseView, TemplateView):
    template_name = "service_api/reports/report.html"

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        report_instances = {}
        for _model, _form in (
            (EducationalAndMethodicalWork, EducationalAndMethodicalWorkForm),
            (ScientificAndInnovativeWork, ScientificAndInnovativeWorkForm),
            (OrganizationalAndEducationalWork, OrganizationalAndEducationalWorkForm),
        ):
            report_instances[_model.slug()] = None
            if hasattr(self.generic_report, _model.__name__.lower()):
                report_instances[_model.slug()] = _form(instance=getattr(self.generic_report, _model.__name__.lower()))

        data.update(
            {
                **report_instances,
                "is_editable": False,
                "is_pdf": True,
                GenericReportData.slug(): GenericReportDataForm(instance=self.generic_report)
                if self.generic_report
                else None,
                "report_name": f"Рейтингові бали {self.request.user.profile.last_name_and_initial} "
                f"за {self.report_period} навчальний рік",
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
                "Content-Disposition": f"attachment; filename=Звітний період {report_period.report_period}.csv".encode(
                    "utf-8"
                )
            },
        )
        response.write(codecs.BOM_UTF8)

        fake_report = type("fake_report", (), {"adjusted_result": 0.0})

        writer = csv.writer(response)
        writer.writerow(
            [
                "#",
                "ПІБ",
                "Кафедра",
                "Факультет",
                "Посада",
                "Відпрацьовано Місяців",
                "Доля Ставки",
                "Підсумковий Бал",
                EducationalAndMethodicalWork.NAME,
                ScientificAndInnovativeWork.NAME,
                OrganizationalAndEducationalWork.NAME,
            ]
        )
        for i, one in enumerate(self.get_qs(), start=1):
            if self.is_valid(one):
                writer.writerow(
                    [
                        i,
                        one.user.profile.last_name_and_initial,
                        one.user.profile.department,
                        one.user.profile.department.faculty,
                        one.user.profile.position,
                        one.assignment_duration,
                        one.assignment,
                        one.result,
                        getattr(one, "educationalandmethodicalwork", fake_report).adjusted_result,
                        getattr(one, "scientificandinnovativework", fake_report).adjusted_result,
                        getattr(one, "organizationalandeducationalwork", fake_report).adjusted_result,
                    ]
                )

        self.__response = response

    @property
    def response(self):
        return self.__response


@login_required
def pivot_report_by_type(request, report_period_id, level_type=None, pk=None):
    report = PivotReport(request, report_period_id=report_period_id, level_type=level_type, pk=pk)
    report.prepare_response()
    return report.response


class ReportView(View):
    REPORT_MODEL: None

    def get_headers(self) -> list[str]:
        raise NotImplementedError

    def get_values(self, report: "REPORT_MODEL") -> list[str]:
        raise NotImplementedError

    def get_qs(self, report_period: ReportPeriod, faculty_id: int = None, department_id: int = None):
        raise NotImplementedError

    def get(self, request, report_period_id: int, faculty_id: int = None, department_id: int = None):
        report_period = ReportPeriod.objects.get(pk=report_period_id)
        response = HttpResponse(
            content_type="text/csv",
            headers={
                "Content-Disposition": f"attachment; filename={self.REPORT_MODEL.file_name}_{report_period.report_period}.csv"
            },
        )
        response.write(codecs.BOM_UTF8)

        writer = csv.writer(response)
        writer.writerow(self.get_headers())
        for t_result in self.get_qs(report_period, faculty_id, department_id):
            writer.writerow(self.get_values(t_result))
        return response


class TeachersReportView(ReportView):
    REPORT_MODEL = TeacherResults

    def get_headers(self):
        return [
            "Місце",
            "ПІБ",
            "Кафедра",
            "Факультет",
            "Посада",
            "Розрахована сума місць робіт",
            "Чистий Бал " + EducationalAndMethodicalWork.NAME,
            "Бал " + EducationalAndMethodicalWork.NAME,
            "Місце " + EducationalAndMethodicalWork.NAME,
            "Чистий Бал " + ScientificAndInnovativeWork.NAME,
            "Бал " + ScientificAndInnovativeWork.NAME,
            "Місце " + ScientificAndInnovativeWork.NAME,
            "Чистий Бал " + OrganizationalAndEducationalWork.NAME,
            "Бал " + OrganizationalAndEducationalWork.NAME,
            "Місце " + OrganizationalAndEducationalWork.NAME,
            "Відпрацьовано місяців",
            "Доля ставки",
            "Cтудентський бал",
        ]

    def get_values(self, report: REPORT_MODEL):
        return [
            report.place,
            report.generic_report_data.user.profile.last_name_and_initial,
            report.generic_report_data.user.profile.department,
            report.generic_report_data.user.profile.department.faculty,
            report.generic_report_data.user.profile.position,
            report.scores_sum,
            report.generic_report_data.educationalandmethodicalwork.result,
            report.generic_report_data.educationalandmethodicalwork.adjusted_result,
            report.educationalandmethodicalwork_place,
            report.generic_report_data.scientificandinnovativework.result,
            report.generic_report_data.scientificandinnovativework.adjusted_result,
            report.scientificandinnovativework_place,
            report.generic_report_data.organizationalandeducationalwork.result,
            report.generic_report_data.organizationalandeducationalwork.adjusted_result,
            report.organizationalandeducationalwork_place,
            report.generic_report_data.assignment_duration,
            report.generic_report_data.assignment,
            report.generic_report_data.students_rating,
        ]

    def get_qs(self, report_period: ReportPeriod, faculty=None, department=None):
        return self.REPORT_MODEL.objects.filter(generic_report_data__report_period=report_period).order_by("place")


class HeadsOfDepartmentsReportView(ReportView):
    REPORT_MODEL = HeadsOfDepartmentsResults

    def get_headers(self):
        return [
            "Місце",
            "ПІБ",
            "Кафедра",
            "Факультет",
            "Посада",
            "Сума балів кафедри",
            "Кількість працівників кафедри",
            "Особисті бали",
            "Отримані бали",
        ]

    def get_values(self, report: REPORT_MODEL) -> list[str]:
        return [
            report.place,
            report.teacher_result.generic_report_data.user.profile.last_name_and_initial,
            report.teacher_result.generic_report_data.user.profile.department,
            report.teacher_result.generic_report_data.user.profile.department.faculty,
            report.teacher_result.generic_report_data.user.profile.position,
            report.related_to_department_sum,
            report.related_to_department_count,
            report.teacher_result.scores_sum,
            report.scores_sum,
        ]

    def get_qs(self, report_period: ReportPeriod, faculty=None, department=None):
        return self.REPORT_MODEL.objects.filter(
            teacher_result__generic_report_data__report_period=report_period
        ).order_by("place")


class FacultiesReportView(ReportView):
    REPORT_MODEL = FacultyResults

    def get_headers(self):
        return [
            "Місце",
            "Факультет",
            "Сума місць факультету",
            "Кількість працівників факультету",
            "Середній бал факультету",
        ]

    def get_values(self, report: REPORT_MODEL) -> list[str]:
        return [
            report.place,
            report.faculty.title,
            report.places_sum,
            report.places_sum_count,
            report.places_sum_average,
        ]

    def get_qs(self, report_period: ReportPeriod, faculty=None, department=None):
        return self.REPORT_MODEL.objects.filter(report_period=report_period).order_by("place")


class DecansReportView(ReportView):
    REPORT_MODEL = DecansResults

    def get_headers(self):
        return [
            "Місце",
            "ПІБ",
            "Кафедра",
            "Факультет",
            "Посада",
            "Сума балів деканату",
        ]

    def get_values(self, report: REPORT_MODEL) -> list[str]:
        return [
            report.place,
            report.teacher_result.generic_report_data.user.profile.last_name_and_initial,
            report.teacher_result.generic_report_data.user.profile.department,
            report.teacher_result.generic_report_data.user.profile.department.faculty,
            report.teacher_result.generic_report_data.user.profile.position,
            report.sum_place,
        ]

    def get_qs(self, report_period: ReportPeriod, faculty=None, department=None):
        return self.REPORT_MODEL.objects.filter(
            teacher_result__generic_report_data__report_period=report_period
        ).order_by("place")

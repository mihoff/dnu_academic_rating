from django.forms import ModelForm
from django.forms.utils import ErrorList
from django.utils.html import format_html

from service_api.models import GenericReportData, EducationalAndMethodicalWork, OrganizationalAndEducationalWork, \
    ScientificAndInnovativeWork


class DivErrorList(ErrorList):
    def __str__(self):
        return self.as_divs()

    def as_divs(self):
        if not self:
            return ''
        return format_html(
            f"""
            <div class="alert alert-danger">
                {"".join([str(e) for e in self])}
                <button type="button" class="close" data-dismiss="alert" aria-label="Close">
                    <span aria-hidden="true">&times;</span>
                </button>
            </div>
        """)


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.initial:
            for f in self.fields.values():
                f.initial = None
                f.required = False
        self.error_class = DivErrorList
        for visible in self.visible_fields():
            visible.field.widget.attrs["class"] = "form-control form-control-sm"

    def clean(self):
        super().clean()
        if not self.initial:
            for f_name, f_value in self.cleaned_data.items():
                attr = getattr(self._meta.model, f_name)
                self.cleaned_data[f_name] = f_value or attr.field.default
        return self.cleaned_data


class GenericReportDataForm(BaseForm):
    class Meta:
        model = GenericReportData
        fields = ("assignment_duration", "assignment", "students_rating")


class EducationalAndMethodicalWorkForm(BaseForm):
    class Meta:
        model = EducationalAndMethodicalWork
        exclude = ("generic_report_data", "result", "adjusted_result", "place")


class ScientificAndInnovativeWorkForm(BaseForm):
    class Meta:
        model = ScientificAndInnovativeWork
        exclude = ("generic_report_data", "result", "adjusted_result", "place")


class OrganizationalAndEducationalWorkForm(BaseForm):
    class Meta:
        model = OrganizationalAndEducationalWork
        exclude = ("generic_report_data", "result", "adjusted_result", "place")

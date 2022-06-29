from datetime import datetime

from django.contrib import admin
from django.contrib.auth.models import User
from django.core import validators
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from service_api.calculations import BaseCalculation
from system_app.models import Documents

YES_SVG = f"<img src='{static('admin/img/icon-yes.svg')}' alt='False'>"
NO_SVG = f"<img src='{static('admin/img/icon-no.svg')}' alt='False'>"


def number_semicolon_validator(value):
    try:
        [int(i) for i in value.split(";")]
    except:
        raise ValidationError("Невірний формат даних. Введіть цілі числа через крапку з комою.")


def float_number_semicolon_validator(value):
    try:
        [float(i.replace(",", ".")) for i in value.split(";")]
    except:
        raise ValidationError("Невірний формат даних. Введіть цілі або дробні числа через крапку з комою.")


def float_number_brackets_float_number_semicolon_validator(value):
    try:
        if value != "0":
            for i in value.split(";"):
                v, k = i.split("(")
                float(v.replace(",", "."))
                float(k.replace(")", "").replace(",", "."))
    except:
        raise ValidationError(
            "Невірний формат даних. Цілі або дробні пари чисел в форматі V(K) "
            "та розділені крапкою із комою в разі декількох пар"
        )


class BaseReportModel(models.Model):
    adjust_rate = 1

    generic_report_data = models.OneToOneField("GenericReportData", on_delete=models.CASCADE, blank=True, null=True)
    result = models.FloatField(verbose_name="Підсумковий бал", default=0, validators=[validators.MinValueValidator(0)])
    adjusted_result = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Додано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Останнє редагування")

    @property
    def report_period(self) -> str:
        return self.generic_report_data.report_period.report_period

    @staticmethod
    def raw_calculation(raw_result, generic_report):
        try:
            # Корекция базовых баллов относительно ставки
            assignment_correction = raw_result / generic_report.assignment

            # Коррекция баллов относительно колличества отработанних месяцев
            result = assignment_correction / (generic_report.assignment_duration / 10)
        except (ZeroDivisionError, AttributeError):
            result = 0.0
        return BaseCalculation.apply_rounding(result)

    def get_final_result(self) -> float:
        return self.raw_calculation(self.result, self.generic_report_data)

    class Meta:
        abstract = True


class ReportPeriod(models.Model):
    REPORT_PERIOD_CHOICES = [(f"{i}/{i + 1}", f"{i}/{i + 1}") for i in range(2020, 2030, 1)]

    is_active = models.BooleanField(verbose_name="Активний", default=False)
    report_period = models.CharField(verbose_name="Період", max_length=9, choices=REPORT_PERIOD_CHOICES)

    annual_workload = models.FloatField(
        verbose_name="середньорічне навчальне навантаження в ДНУ (год.)",
        default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(600)],
    )
    document = models.ForeignKey(Documents, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.report_period

    @staticmethod
    def get_active():
        return ReportPeriod.objects.filter(is_active=True).first()

    @staticmethod
    def get_current_report_period():
        _today = datetime.today()
        if _today > datetime(_today.year, month=7, day=1):
            return f"{_today.year}/{_today.year + 1}"
        return f"{_today.year - 1}/{_today.year}"

    class Meta:
        verbose_name = "Звітній період"
        verbose_name_plural = "Звітні періоди"
        constraints = [UniqueConstraint(fields=["report_period"], name="unique_report_period_report_period")]


class GenericReportData(models.Model):
    NAME = "Загальні дані"

    REPORT_PERIOD_CHOICES = [(f"{i}/{i + 1}", f"{i}/{i + 1}") for i in range(2020, 2030, 1)]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    report_period = models.ForeignKey(ReportPeriod, on_delete=models.SET_NULL, blank=True, null=True)
    result = models.FloatField(default=0, validators=[validators.MinValueValidator(0)], verbose_name="Підсумковий бал")
    is_closed = models.BooleanField(verbose_name="Чи закрито звітний період", default=False)

    assignment_duration = models.FloatField(
        verbose_name="Кількість відпрацьованих місяців за звітний період",
        default=10,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(10)],
        help_text="Значення від 0 до 10",
    )

    assignment = models.FloatField(
        verbose_name="Доля ставки, яку обіймає за основною посадою або за штатним сумісництвом",
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(1)],
        default=1,
        help_text="Значення від 0 до 1",
    )
    students_rating = models.FloatField(
        verbose_name="Бал за наслідками анонімного анкетування студентів",
        default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(200)],
        help_text="Значення від 0 до 200 балів. "
        "Сума балів, які отримані НПП за результатами двох анкетувань (1 та 2 семестр)",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Додано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Останнє редагування")

    def __str__(self):
        return self.NAME

    @staticmethod
    def get_report(user, report_period):
        return GenericReportData.objects.filter(user=user, report_period__report_period=report_period).first()

    @staticmethod
    def slug():
        return "generic_report_data"

    @admin.display(description="Всі звіти")
    def admin_reports(self):
        report_conditions = [
            f"{r.NAME}{YES_SVG if getattr(self, r.__name__.lower(), False) else NO_SVG}" for r in REPORT_MODELS
        ]
        return mark_safe("<br/>".join(report_conditions))

    def all_reports_done(self):
        return all(getattr(self, r.__name__.lower(), False) for r in REPORT_MODELS)

    class Meta:
        verbose_name = "Загальний звіт"
        verbose_name_plural = "Загальні звіти"
        constraints = [UniqueConstraint(fields=["user", "report_period"], name="unique_user_report_period")]


class EducationalAndMethodicalWork(BaseReportModel):
    """
    1. Навчально-методична робота
    """

    NAME = "Навчально-методична робота"

    NONE = None
    HONORED_WORKER_OF_EDUCATION_OF_UKRAINE = "honored_worker_of_education_of_ukraine"
    EXCELLENT_EDUCATION = "excellent_education"
    HONORED_PROFESSOR_LECTURER_OF_DNU = "honored_professor_lecturer_of_dnu"
    HONORED_LECTURER_OF_DNU = "honored_lecturer_of_dnu"
    PROFESSOR = "professor"
    DOCENT = "docent"
    POSITION_CHOICES = (
        (NONE, "Не отримано"),
        (HONORED_WORKER_OF_EDUCATION_OF_UKRAINE, "Заслужений працівник освіти України"),
        (EXCELLENT_EDUCATION, "Відмінник освіти"),
        (HONORED_PROFESSOR_LECTURER_OF_DNU, "Заслужений професор(викладач) ДНУ"),
        (HONORED_LECTURER_OF_DNU, "Заслужений викладач ДНУ"),
        (PROFESSOR, "Професор"),
        (DOCENT, "Доцент"),
    )

    LEVEL_ONE = "І освітній рівень"
    LEVEL_TWO = "ІІ освітній рівень"
    LEVEL_THREE = "ІІІ освітній рівень"
    LEVELS_CHOICES = ((NONE, "-"), (LEVEL_ONE, LEVEL_ONE), (LEVEL_TWO, LEVEL_TWO), (LEVEL_THREE, LEVEL_THREE))

    # 1 Виконання навчального навантаження
    one_one = models.FloatField(
        verbose_name="обсяг виконаного аудиторного навантаження (год.)",
        default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(600)],
        help_text="До аудиторного навантаження включаються години за проведення лекційних, практичних, семінарських, "
        "лабораторних занять.",
    )
    one_two = models.FloatField(
        verbose_name="обсяг виконаного аудиторного навантаження (год.) іноземною мовою",
        default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(600)],
    )
    one_three = models.FloatField(
        verbose_name="загальне навчальне навантаження працівника (год.) за рік",
        default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(600)],
    )

    # 2 Розробка та затвердження нової освітньої (освітньо-професійної або освітньо-наукової) програми
    two_one = models.CharField(
        max_length=256,
        verbose_name="розробка та затвердження",
        default="0",
        validators=[float_number_semicolon_validator],
    )
    two_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[float_number_semicolon_validator]
    )

    # 3 Розробка нових
    three_one = models.CharField(
        max_length=256, verbose_name="навчальних планів", default="0", validators=[number_semicolon_validator]
    )
    three_two = models.CharField(
        max_length=256, verbose_name="робочих навчальних планів", default="0", validators=[number_semicolon_validator]
    )
    three_three = models.CharField(
        max_length=256, verbose_name="навчальних планів", default="0", validators=[number_semicolon_validator]
    )
    three_four = models.CharField(
        max_length=256, verbose_name="робочих навчальних планів", default="0", validators=[number_semicolon_validator]
    )

    # 4 Виконання обов’язків гаранта ОП І освітнього рівня/ІІ ОР/ІІІ ОР
    four_one = models.CharField(
        max_length=32, verbose_name="", choices=LEVELS_CHOICES, default=NONE, null=True, blank=True
    )

    # 5 Підготовка справи та успішне проходження експертизи
    five_one = models.CharField(
        max_length=256, verbose_name="ліцензійної", default="0", validators=[float_number_semicolon_validator]
    )
    five_two = models.CharField(
        max_length=256, verbose_name="акредитаційної", default="0", validators=[float_number_semicolon_validator]
    )

    # 6 Публікації
    six_one = models.CharField(
        max_length=256,
        verbose_name="курс лекцій",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    six_two = models.CharField(
        max_length=256,
        verbose_name="навчально-методичні рекомендації",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    six_three = models.CharField(
        max_length=256,
        verbose_name="підручник в Україні",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    six_four = models.CharField(
        max_length=256,
        verbose_name="навчальний посібник в Україні",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    six_five = models.CharField(
        max_length=256,
        verbose_name="підручник за кордоном офіційною мовою ЄС",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    six_six = models.CharField(
        max_length=256,
        verbose_name="навчальний посібник за кордоном офіційною мовою ЄС",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )

    # 7 Редагування та переклад підручників, навчальних посібників, методичних матеріалів тощо
    seven_one = models.CharField(
        max_length=256, verbose_name="редагування", default="0", validators=[float_number_semicolon_validator]
    )
    seven_two = models.CharField(
        max_length=256, verbose_name="переклад", default="0", validators=[float_number_semicolon_validator]
    )

    # 8 Розробка та оновлення робочої програми навчальної дисципліниза умови відповідного затвердження
    # та розміщення на сайті (у разі введення нової дисципліни)
    eight_one = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[float_number_semicolon_validator]
    )
    eight_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[float_number_semicolon_validator]
    )

    # 9 Підготовка нової (оновлення) лекційної презентації
    nine_one = models.IntegerField(verbose_name="розробка", default=0)
    nine_two = models.IntegerField(verbose_name="оновлення", default=0)

    # 10 Розробка і підготовка нових лабораторних робіт на лабораторному устаткуванні
    ten_one = models.CharField(
        max_length=256, verbose_name="розробка і підготовка", default="0", validators=[float_number_semicolon_validator]
    )
    ten_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[float_number_semicolon_validator]
    )

    # 11 Розробка і підготовка нових лабораторних робіт на лабораторному устаткуванні
    eleven_one = models.IntegerField(verbose_name="розробка і підготовка", default=0)
    eleven_two = models.IntegerField(verbose_name="оновлення", default=0)

    # 12 Підготовка комп’ютерного програмного забезпечення навчальних дисциплін
    twelve_one = models.CharField(
        max_length=256, verbose_name="підготовка", default="0", validators=[float_number_semicolon_validator]
    )
    twelve_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[float_number_semicolon_validator]
    )

    # 13 Розробка і впровадження нових форм, методів і технологій навчання,
    # зокрема, інтерактивних методів навчання (ділових ігор, ситуативних вправ, кейс-методів, тощо)
    thirteen_one = models.CharField(
        max_length=256,
        verbose_name="розробка і впровадження",
        default="0",
        validators=[float_number_semicolon_validator],
    )

    # 14 Розробка складових електронних освітніх ресурсів (ЕОР)
    # відповідно до положення за умови розміщення на ресурсі ДНУ
    fourteen_one = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[float_number_semicolon_validator]
    )
    fourteen_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[float_number_semicolon_validator]
    )

    # 15 Розробка програм і завдань до вступних випробувань
    fifteen_one = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[float_number_semicolon_validator]
    )
    fifteen_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[float_number_semicolon_validator]
    )
    fifteen_three = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[float_number_semicolon_validator]
    )
    fifteen_four = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[float_number_semicolon_validator]
    )
    fifteen_five = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[float_number_semicolon_validator]
    )
    fifteen_six = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[float_number_semicolon_validator]
    )

    # 16 Рецензування навчально-методичних матеріалів
    sixteen_one = models.CharField(
        max_length=256,
        verbose_name="Підручників, навчально-методичних посібників, посібників",
        default="0",
        validators=[float_number_semicolon_validator],
    )
    sixteen_two = models.CharField(
        max_length=256,
        verbose_name="навчально-методичних матеріалів (підручників, посібників тощо), "
        "що подаються МОН України на закрите рецензування",
        default="0",
        validators=[float_number_semicolon_validator],
    )

    # 17 Експертиза
    seventeen_one = models.IntegerField(
        verbose_name="нормативних документів, наданих МОН України для публічного обговорення",
        default=0,
        validators=[validators.MinValueValidator(0)],
    )
    seventeen_two = models.IntegerField(
        verbose_name="конкурсних дипломних проєктів і робіт", default=0, validators=[validators.MinValueValidator(0)]
    )
    seventeen_three = models.IntegerField(
        verbose_name="конкурсних робіт МАН", default=0, validators=[validators.MinValueValidator(0)]
    )

    # 18 Виконання робіт за міжнародними договорами, зокрема програми двох дипломів, контрактами,
    # проектами ТEMPUS, ERASMUS+
    # выконавець True - False
    eighteen_one = models.BooleanField(verbose_name="Керівник", default=False)
    eighteen_two = models.IntegerField(verbose_name="Кількість виконвавців проєкту", default=0)

    # 19 Підготовка концертних програм і персональних художніх виставок, спортивних заходів
    nineteen_one = models.IntegerField(default=0, verbose_name="міжнародного рівня")
    nineteen_two = models.IntegerField(default=0, verbose_name="всеукраїнського рівня")
    nineteen_three = models.IntegerField(default=0, verbose_name="регіонального рівня")

    # 20 Підготовка лауреата виставки, творчого конкурсу для творчих спеціальностей
    # (для кафедр творчого спрямування)
    twenty_one = models.IntegerField(default=0, verbose_name="міжнародного рівня")
    twenty_two = models.IntegerField(default=0, verbose_name="всеукраїнського рівня")
    twenty_three = models.IntegerField(default=0, verbose_name="регіонального рівня")

    # 21 Підготовка призера змагань (для викладачів кафедри фізичного виховання і спорту)
    twenty_one_one = models.IntegerField(default=0, verbose_name="олімпіади, чемпіонату світу")
    twenty_one_two = models.IntegerField(default=0, verbose_name="чемпіонату Європи")
    twenty_one_three = models.IntegerField(default=0, verbose_name="чемпіонату України")

    # 22 Підготовка учасника змагань (для викладачів кафедри фізичного виховання і спорту)
    twenty_two_one = models.IntegerField(default=0, verbose_name="олімпіади, чемпіонату світу")
    twenty_two_two = models.IntegerField(default=0, verbose_name="чемпіонату Європи")

    # 23 Отримання звання
    twenty_three_one = models.CharField(max_length=50, choices=POSITION_CHOICES, default=NONE, null=True, blank=True)

    @staticmethod
    def get_report(user, report_period: ReportPeriod):
        return EducationalAndMethodicalWork.objects.filter(
            generic_report_data__user=user, generic_report_data__report_period=report_period
        ).first()

    @staticmethod
    def slug():
        return "educational_and_methodical_work"

    @property
    def report_period_url(self):
        return self.generic_report_data.report_period.report_period.replace("/", "-")

    def bool_admin(self):
        return bool(self)

    def __str__(self):
        return self.NAME

    class Meta:
        verbose_name = 'Звіт "Навчально-методична робота"'
        verbose_name_plural = 'Звіти "Навчально-методична робота"'


class ScientificAndInnovativeWork(BaseReportModel):
    NAME = "Науково-інноваційна робота"

    one_one = models.FloatField(
        verbose_name="Загальне значення", default=0, validators=[validators.MinValueValidator(0)]
    )

    @staticmethod
    def get_report(user, report_period: ReportPeriod):
        return ScientificAndInnovativeWork.objects.filter(
            generic_report_data__user=user, generic_report_data__report_period=report_period
        ).first()

    @staticmethod
    def slug():
        return "scientific_and_innovative_work"

    @property
    def report_period(self):
        return self.generic_report_data.report_period.report_period

    def __str__(self):
        return self.NAME

    class Meta:
        verbose_name = f'Звіт "Науково-інноваційна робота"'
        verbose_name_plural = 'Звіти "Науково-інноваційна робота"'


class OrganizationalAndEducationalWork(BaseReportModel):
    """
    3. Організаційно-виховна робота
    """

    NAME = "Організаційно-виховна робота"

    NONE = None
    HEAD = "head"
    SECRETARY = "secretary"
    MEMBER = "member"
    POSITION_CHOICES = (
        (NONE, "-"),
        (HEAD, "голова, заступник голови"),
        (SECRETARY, "секретар"),
        (MEMBER, "член"),
    )

    adjust_rate = 2

    # 1. Робота в науково-методичних комісіях (підкомісіях) з вищої освіти Міністерства освіти і науки України
    one_one = models.CharField(
        max_length=10, verbose_name="посада", default=NONE, choices=POSITION_CHOICES, blank=True, null=True
    )

    # 2. Робота в Акредитаційній комісії або її експертних рад, галузевих експертних радах НАЗЯВО, або Міжгалузевої
    # експертної ради з вищої освіти Акредитаційної комісії, експертних комісіях МОН/зазначеного агентства
    two_one = models.BooleanField(default=False)

    # 3. Робота в експертних комісіях АКУ та ліцензування МОН
    three_one = models.BooleanField(default=False)

    # 4. Робота в науково-технічній раді НДЧ ДНУ, науково-методичній раді, РЗЯВО, БЗЯВО університету (факультету)
    four_one = models.CharField(
        verbose_name="Робота в науково-технічній раді НДЧ ДНУ",
        max_length=10,
        choices=POSITION_CHOICES,
        default=NONE,
        blank=True,
        null=True,
    )
    four_two = models.CharField(
        verbose_name="Робота в науково-методичній раді",
        max_length=10,
        choices=POSITION_CHOICES,
        default=NONE,
        blank=True,
        null=True,
    )
    four_three = models.CharField(
        verbose_name="Робота в науково-методичній раді",
        max_length=10,
        choices=POSITION_CHOICES,
        default=NONE,
        blank=True,
        null=True,
    )
    four_four = models.CharField(
        verbose_name="Робота в раді та бюро із забезпечення якості вищої освіти (РЗЯВО, БЗЯВО)",
        max_length=10,
        choices=POSITION_CHOICES,
        default=NONE,
        blank=True,
        null=True,
    )
    four_five = models.CharField(
        verbose_name="Робота в раді та бюро із забезпечення якості вищої освіти (РЗЯВО, БЗЯВО)",
        max_length=10,
        choices=POSITION_CHOICES,
        default=NONE,
        blank=True,
        null=True,
    )
    four_six = models.CharField(
        verbose_name="Робота у бюро з академічної доброчесності факультету",
        max_length=10,
        choices=POSITION_CHOICES,
        default=NONE,
        blank=True,
        null=True,
    )

    # 5. Організація та проведення загальнодержавних наукових конференцій, симпозіумів і семінарів
    five_one = models.IntegerField(verbose_name="голова оргкомітету", default=0)
    five_two = models.IntegerField(verbose_name="вчений секретар оргкомітету", default=0)
    five_three = models.IntegerField(verbose_name="член оргкомітету", default=0)

    # 6. Виконання обов’язків заступника декана факультету на громадських засадах
    # з навчальної роботи (з інших видів діяльності)
    six_one = models.BooleanField(verbose_name="навчальна робота", default=False)
    six_two = models.BooleanField(verbose_name="інші види діяльності", default=False)

    # 7. Робота секретарем ЕК
    seven_one = models.IntegerField(verbose_name="кількість відпрацьованих днів", default=0)

    # 8. Здійснення процедур нормоконтролю випускних кваліфікаційних робіт
    eight_one = models.IntegerField(verbose_name="кількість перевірених робіт", default=0)

    # 9. Перевірка випускних кваліфікаційних робіт на плагіат
    nine_one = models.IntegerField(verbose_name="кількість робіт", default=0)

    # 10. Виконання обов’язків відповідального за організацію замовлення додатків DIPLOMA SUPLIMENT,
    # включаючи переклад на іноземну мову
    ten_one = models.IntegerField(verbose_name="кількість студентів, яким замовлено додатки", default=0)

    # 11. Участь у виховній роботі в студентському колектив
    eleven_one = models.IntegerField(
        verbose_name="Виконання обов’язків куратора (наставника) академічної групи", default=0
    )
    eleven_two = models.BooleanField(verbose_name="проведення виховної роботи в гуртожитках", default=False)

    # 12. Робота у складі вченої ради ДНУ
    twelve_one = models.BooleanField(default=False)

    # 13. Робота у складі вченої ради факультету
    thirteen_one = models.CharField(
        verbose_name="Робота у складі вченої ради факультету",
        choices=POSITION_CHOICES,
        default=NONE,
        blank=True,
        null=True,
        max_length=10,
    )

    # 14 Відповідальна особа із забезпечення діяльності разової спеціалізованої вченої ради
    fourteen_one = models.IntegerField(verbose_name="Кількість захищених робіт", default=0)

    # 15. Організаційна робота
    fifteen_one = models.BooleanField(
        verbose_name="завідувача кафедри (у тому числі відвідування занять завідувачем кафедри зі складанням відгуку, "
        "проведення засідань кафедри, участь у засіданнях  деканату факультету)",
        default=False,
    )
    fifteen_two = models.BooleanField(verbose_name="заступник завідувача кафедри на громадських засадах", default=False)

    # 16. Участь у профорієнтаційній роботі кафедри, факультету, університету
    sixteen_one = models.IntegerField(verbose_name="кількість заходів", default=0)

    # 17. Робота в приймальній комісії (відповідно до наказів)
    seventeen_one = models.BooleanField(verbose_name="відповідальний секретар", default=False)
    seventeen_two = models.BooleanField(verbose_name="заступник відповідального секретаря", default=False)
    seventeen_three = models.BooleanField(
        verbose_name="голова предметної екзаменаційної комісії, комісії зі співбесіди", default=False
    )
    seventeen_four = models.IntegerField(verbose_name="робота у відбірковій комісії", default=0)
    seventeen_five = models.IntegerField(
        verbose_name="член комісії зі співбесіді, предметної екзаменаційної комісії", default=0
    )
    seventeen_six = models.IntegerField(
        verbose_name="робота у групі контролю й введення даних до ЄДЕБО (відповідальний за введення даних до ЄДЕБО)",
        default=0,
    )
    seventeen_seven = models.IntegerField(
        verbose_name="робота у складі асистентської групи приймальної комісії", default=0
    )
    seventeen_eight = models.IntegerField(verbose_name="робота в апеляційній комісії", default=0)

    # 18. Введення персональних даних викладачів в ЄДЕБО та їхня періодична актуалізація, а також перевірка
    # персональних даних студентів випускних курсів, що виконують співробітники на факультетах протягом
    # навчального року (окрім роботи в межах діяльності приймальної комісії)
    eighteen_one = models.BooleanField(default=False)

    # 19. Участь у підготовці та проведенні студентських та учнівських олімпіад, турнірів, конкурсів,
    # олімпіад ДНУ для вступників
    nineteen_one = models.IntegerField(default=0)

    # 20. Участь в організації та проведенні позанавчальних культурно-спортивних заходів
    twenty_zero_one = models.IntegerField(default=0)

    # 21. Робота на виборних посадах у профспілковому комітеті ДНУ
    twenty_one_one = models.BooleanField(default=False)

    # 22. Керівництво волонтерським проектом студентів
    twenty_two_one = models.BooleanField(default=False)

    # 23 Розроблення нормативних документів ДНУ з питань організації навчальної, наукової,
    # науково-дослідної, виховної роботи, міжнародної діяльності тощо
    twenty_three_one = models.CharField(
        max_length=256,
        verbose_name="Кількість виконавців одного документу",
        default="0",
        validators=[float_number_semicolon_validator],
    )

    # 24 Адміністрування офіційної вебсторінки факультету, кафедри, збірника наукових праць, фахового журналу,
    # програмного забезпечення рейтингу, репозиторію, системи office 365 факультету
    twenty_four_one = models.IntegerField(verbose_name="кількість видів робіт", default=0)

    # 25 Керівництво збірною
    twenty_five_one = models.BooleanField(verbose_name="ДНУ", default=False)

    # 26 Тренер збірної
    twenty_six_one = models.BooleanField(verbose_name="України", default=False)
    twenty_six_two = models.BooleanField(verbose_name="області", default=False)

    # 27 Головний суддя змагань
    twenty_seven_one = models.BooleanField(verbose_name="міжнародних", default=False)
    twenty_seven_two = models.BooleanField(verbose_name="національних", default=False)
    twenty_seven_three = models.BooleanField(verbose_name="обласних", default=False)

    @staticmethod
    def get_report(user, report_period):
        return OrganizationalAndEducationalWork.objects.filter(
            generic_report_data__user=user, generic_report_data__report_period__report_period=report_period
        ).first()

    @staticmethod
    def slug():
        return "organizational_and_educational_work"

    def __str__(self):
        return self.NAME

    class Meta:
        verbose_name = 'Звіт "Організаційно-виховна робота"'
        verbose_name_plural = 'Звіти "Організаційно-виховна робота"'


REPORT_MODELS = (EducationalAndMethodicalWork, ScientificAndInnovativeWork, OrganizationalAndEducationalWork)

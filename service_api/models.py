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
from user_profile.models import Faculty

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
            # # Корекция базовых баллов относительно ставки
            # result = raw_result / generic_report.assignment

            # Коррекция баллов относительно колличества отработанних месяцев
            result = raw_result / (generic_report.assignment_duration / 10)
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

    # 2 Розробка та затвердження нової освітньої (освітньо-професійної або освітньо-наукової) програми (нова редакція)
    two_one = models.IntegerField(
        verbose_name="гарант", default=0, validators=[validators.MinValueValidator(0)]
    )
    two_two = models.IntegerField(
        verbose_name="розробник", default=0, validators=[validators.MinValueValidator(0)]
    )
    two_three = models.IntegerField(
        verbose_name="гарант", default=0, validators=[validators.MinValueValidator(0)]
    )
    two_four = models.IntegerField(
        verbose_name="розробник", default=0, validators=[validators.MinValueValidator(0)]
    )

    # 3 Розробка нових навчальних планів
    three_one = models.IntegerField(verbose_name="розробка", default=0, validators=[validators.MinValueValidator(0)])
    three_two = models.IntegerField(verbose_name="оновлення", default=0, validators=[validators.MinValueValidator(0)])

    # 4 Виконання обов’язків гаранта ОП І освітнього рівня/ ІІ ОР/ ІІІ ОР
    four_one = models.CharField(
        max_length=32, verbose_name="", choices=LEVELS_CHOICES, default=NONE, null=True, blank=True
    )

    # 5 Підготовка справи та успішне проходження експертизи
    five_one = models.IntegerField(verbose_name="відповідальна особа", default=0, validators=[validators.MinValueValidator(0)])
    five_two = models.IntegerField(verbose_name="виконавець", default=0, validators=[validators.MinValueValidator(0)])
    five_three = models.IntegerField(verbose_name="відповідальна особа", default=0, validators=[validators.MinValueValidator(0)])
    five_four = models.IntegerField(verbose_name="виконавець", default=0, validators=[validators.MinValueValidator(0)])

    # 6 Публікації видань методичних матеріалів:
    six_one = models.CharField(
        max_length=256,
        verbose_name="публікація",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    six_two = models.CharField(
        max_length=256,
        verbose_name="повторне видання",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    six_three = models.CharField(
        max_length=256,
        verbose_name="публікація",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    six_four = models.CharField(
        max_length=256,
        verbose_name="повторне видання",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )

    # 7 Публікації видань за рекомендацією вченої ради ДНУ:
    seven_one = models.CharField(
        max_length=256,
        verbose_name="публікація",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    seven_two = models.CharField(
        max_length=256,
        verbose_name="повторне видання",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    seven_three = models.CharField(
        max_length=256,
        verbose_name="публікація",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    seven_four = models.CharField(
        max_length=256,
        verbose_name="повторне видання",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    seven_five = models.CharField(
        max_length=256,
        verbose_name="публікація",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    seven_six = models.CharField(
        max_length=256,
        verbose_name="повторне видання",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    seven_seven = models.CharField(
        max_length=256,
        verbose_name="публікація",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )
    seven_eight = models.CharField(
        max_length=256,
        verbose_name="повторне видання",
        default="0",
        validators=[float_number_brackets_float_number_semicolon_validator],
    )

    # 8 Підготовка нової (оновлення) лекційної презентації
    eight_one = models.IntegerField(verbose_name="розробка", default=0, validators=[validators.MinValueValidator(0)])
    eight_two = models.IntegerField(verbose_name="оновлення", default=0, validators=[validators.MinValueValidator(0)])

    # 9 Запровадження у навчальний процес нових лабораторних /практичних  робіт,
    # що потребують використання спеціалізованого лабораторного/програмного забезпечення
    nine_one = models.IntegerField(verbose_name="запровадження", default=0,validators=[validators.MinValueValidator(0)])

    # 10 Розробка програм і завдань до вступних випробувань
    ten_one = models.IntegerField(
        verbose_name="на перший ОР зі скороченим терміном навчання", default=0, validators=[validators.MinValueValidator(0)]
    )
    ten_two = models.IntegerField(
       verbose_name="на перший ОР на базі ПЗСО", default=0, validators=[validators.MinValueValidator(0)]
    )
    ten_three = models.IntegerField(
       verbose_name="на другий ОР", default=0, validators=[validators.MinValueValidator(0)]
    )

    # 11 Рецензування навчально-методичних матеріалів: підручників, навчально-методичних посібників, посібників
    eleven_one = models.IntegerField(verbose_name="рецензування",default=0, validators=[validators.MinValueValidator(0)])

    # 12 Експертиза конкурсних студентських робіт, починаючи з другого туру; конкурсних робіт МАН
    twelve_one = models.IntegerField(
        verbose_name="експертиза",
        default=0,
        validators=[validators.MinValueValidator(0)],
    )

    # 13 Виконання робіт за міжнародними договорами, зокрема програми двох дипломів, контрактами,
    # проектами ТEMPUS, ERASMUS+
    thirteen_one = models.IntegerField(verbose_name="керівник", default=0, validators=[validators.MinValueValidator(0)])
    thirteen_two = models.IntegerField(verbose_name="учасник", default=0, validators=[validators.MinValueValidator(0)])

    # 14 Персональна участь (підготовка та участь студента чи групи студентів) у концертних програмах, 
    # персональних художніх виставках, творчих конкурсах, спортивних змаганнях  
    fourteen_one = models.IntegerField(default=0, verbose_name="персональна участь")
    fourteen_two = models.IntegerField(default=0, verbose_name="підготовка та участь студента чи групи студентів")
    fourteen_three = models.IntegerField(default=0, verbose_name="персональна участь")
    fourteen_four = models.IntegerField(default=0, verbose_name="підготовка та участь студента чи групи студентів")
    fourteen_five = models.IntegerField(default=0, verbose_name="персональна участь")
    fourteen_six = models.IntegerField(default=0, verbose_name="підготовка та участь студента чи групи студентів")

    # 15 Отримання звання
    fifteen_one = models.CharField(max_length=50, choices=POSITION_CHOICES, default=NONE, null=True, blank=True)

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


class TeacherResults(models.Model):
    file_name = "teachers_results"

    generic_report_data = models.OneToOneField(GenericReportData, on_delete=models.CASCADE)

    educationalandmethodicalwork_place = models.IntegerField(null=True, blank=True)
    organizationalandeducationalwork_place = models.IntegerField(null=True, blank=True)
    scientificandinnovativework_place = models.IntegerField(null=True, blank=True)

    scores_sum = models.DecimalField(decimal_places=4, max_digits=10, null=True, blank=True)
    place = models.IntegerField(null=True, blank=True)


class HeadsOfDepartmentsResults(models.Model):
    file_name = "heads_of_departments_results"

    teacher_result = models.OneToOneField(TeacherResults, on_delete=models.CASCADE)

    related_to_department_sum = models.DecimalField(decimal_places=4, max_digits=10, null=True, blank=True)
    related_to_department_count = models.IntegerField(null=True, blank=True)

    scores_sum = models.DecimalField(decimal_places=4, max_digits=10, null=True, blank=True)
    place = models.IntegerField(null=True, blank=True)


class DecansResults(models.Model):
    file_name = "decans_results"

    teacher_result = models.OneToOneField(TeacherResults, on_delete=models.CASCADE)
    sum_place = models.IntegerField(null=True, blank=True)
    place = models.IntegerField(null=True, blank=True)


class FacultyResults(models.Model):
    file_name = "faculty_results"

    report_period = models.ForeignKey(ReportPeriod, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)

    places_sum = models.DecimalField(decimal_places=4, max_digits=10, null=True, blank=True)
    places_sum_count = models.IntegerField(null=True, blank=True)
    places_sum_average = models.DecimalField(decimal_places=4, max_digits=10, null=True, blank=True)

    place = models.IntegerField(null=True, blank=True)


REPORT_MODELS = (EducationalAndMethodicalWork, ScientificAndInnovativeWork, OrganizationalAndEducationalWork)

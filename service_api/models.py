from datetime import datetime

from django.contrib.auth.models import User
from django.core import validators
from django.db import models
from django.db.models import UniqueConstraint
from django.templatetags.static import static
from django.utils.safestring import mark_safe

from service_api.calculations import BaseCalculation

YES_SVG = f"<img src='{static('admin/img/icon-yes.svg')}' alt='False'>"
NO_SVG = f"<img src='{static('admin/img/icon-no.svg')}' alt='False'>"

NUMBER_SEMICOLON_VALIDATOR = validators.RegexValidator(
    r"\d+?(;|$)", message="Невірний формат даних. Введіть числа через крапку з комою.")

NUMBER_BRACKETS_NUMBER_SPACE_VALIDATOR = validators.RegexValidator(
    r"^[\d+(\d+)\s*]+$", message="Невірний формат даних. Введіть числа через пробіл.")

FLOAT_NUMBER_SEMICOLON_VALIDATOR = validators.RegexValidator(
    r"\d+([,.]\d+)?", message="Невірний формат даних. Введіть числа через крапку з комою.")

FLOAT_NUMBER_BRACKETS_FLOAT_NUMBER_SEMICOLON_VALIDATOR = validators.RegexValidator(
    r"^[\d+(,.)\d+(;|$)\s+]+$", message="Невірний формат даних. Введіть числа через пробіл.")


class BaseReportModel(models.Model):
    adjust_rate = 1

    generic_report_data = models.OneToOneField("GenericReportData", on_delete=models.SET_NULL, blank=True, null=True)
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
            result = .0
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
        verbose_name="середньорічне навчальне навантаження в ДНУ (год.)", default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(600)])
    document = models.FileField(
        verbose_name="Положення", upload_to="uploads/service_api/report_period",
        default=None, null=True, max_length=256)

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
    result = models.FloatField(default=0, validators=[validators.MinValueValidator(0)])
    is_closed = models.BooleanField(verbose_name="Чи закрито звітний період", default=False)

    assignment_duration = models.FloatField(
        verbose_name="Кількість відпрацьованих місяців за звітний період", default=10,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(10)],
        help_text="Значення від 0 до 10")

    assignment = models.FloatField(
        verbose_name="Доля ставки, яку обіймає за основною посадою або за штатним сумісництвом",
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(1)],
        default=1, help_text="Значення від 0 до 1"
    )
    students_rating = models.FloatField(
        verbose_name="Бал за наслідками анонімного анкетування студентів", default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(200)],
        help_text="Значення від 0 до 200 балів. "
                  "Сума балів, які отримані НПП за результатами двох анкетувань (1 та 2 семестр)")
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

    def admin_reports(self):
        report_conditions = [
            f"{r.NAME}{YES_SVG if getattr(self, r.__name__.lower(), False) else NO_SVG}" for r in REPORT_MODELS]
        return mark_safe("<br/>".join(report_conditions))

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
    PROFESSOR = "professor"
    DOCENT = "docent"
    POSITION_CHOICES = (
        (NONE, "Не отримано"),
        (PROFESSOR, "Професор"),
        (DOCENT, "Доцент"),
    )

    LEVEL_ONE = "І освітній рівень"
    LEVEL_TWO = "ІІ освітній рівень"
    LEVEL_THREE = "ІІІ освітній рівень"
    LEVELS_CHOICES = (
        (NONE, "-"),
        (LEVEL_ONE, LEVEL_ONE),
        (LEVEL_TWO, LEVEL_TWO),
        (LEVEL_THREE, LEVEL_THREE)
    )

    # 1 Виконання навчального навантаження
    one_one = models.FloatField(
        verbose_name="обсяг виконаного аудиторного навантаження (год.)", default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(600)],
        help_text="До аудиторного навантаження включаються години за проведення лекційних, практичних, семінарських, "
                  "лабораторних занять.")
    one_two = models.FloatField(
        verbose_name="обсяг виконаного аудиторного навантаження (год.) іноземною мовою", default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(600)])
    one_three = models.FloatField(
        verbose_name="загальне навчальне навантаження працівника (год.) за рік", default=0,
        validators=[validators.MinValueValidator(0), validators.MaxValueValidator(600)])

    # 2 Рецензування навчально-методичних матеріалів
    two_one = models.CharField(
        max_length=256, verbose_name="методичних вказівок (рекомендацій)", default="0",
        validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    two_two = models.CharField(
        max_length=256, verbose_name="навчально-методичних посібників, посібників", default="0",
        validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    two_three = models.CharField(
        max_length=256,
        verbose_name="навчально-методичних матеріалів (підручників, посібників тощо), "
                     "що подаються МОН України на закрите рецензування",
        default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 3 Експертиза
    three_one = models.IntegerField(
        verbose_name="нормативних документів, наданих МОН України для публічного обговорення",
        default=0, validators=[validators.MinValueValidator(0)])
    three_two = models.IntegerField(
        verbose_name="конкурсних дипломних проєктів і робіт", default=0, validators=[validators.MinValueValidator(0)])
    three_three = models.IntegerField(
        verbose_name="конкурсних робіт МАН", default=0, validators=[validators.MinValueValidator(0)])

    # 4 Розроблення нормативних документів ДНУ  з питань організації навчальної, наукової, науково-дослідної,
    # виховної роботи, міжнародної діяльності тощо
    four_one = models.CharField(
        max_length=256, verbose_name="кількість виконавців одного документу", default="0",
        validators=[NUMBER_SEMICOLON_VALIDATOR])

    # 5 Редагування (переклад) підручників, навчальних посібників, методичних матеріалів тощо
    five_one = models.CharField(
        max_length=256, verbose_name="редагування (кількість друкованих аркушів)",
        default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    five_two = models.CharField(
        max_length=256, verbose_name="переклад (кількість друкованих аркушів)", default="0",
        validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 6 Виконання робіт за міжнародними договорами, зокрема програми двох дипломів, контрактами,
    # проектами ТEMPUS, ERASMUS+
    # выконавець True - False
    six_one = models.BooleanField(verbose_name="В ролі керівника", default=False)
    six_two = models.IntegerField(verbose_name="В ролі виконавця", default=0, help_text="Кількість участників проєкту")

    # 7 Публікації
    seven_one = models.CharField(
        max_length=256, verbose_name="курс лекцій", default="0",
        validators=[FLOAT_NUMBER_BRACKETS_FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    seven_two = models.CharField(
        max_length=256, verbose_name="навчально-методичні рекомендації", default="0",
        validators=[FLOAT_NUMBER_BRACKETS_FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    seven_three = models.CharField(
        max_length=256, verbose_name="підручник в Україні", default="0",
        validators=[FLOAT_NUMBER_BRACKETS_FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    seven_four = models.CharField(
        max_length=256, verbose_name="навчальний посібник в Україні", default="0",
        validators=[FLOAT_NUMBER_BRACKETS_FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    seven_five = models.CharField(
        max_length=256, verbose_name="підручник за кордоном", default="0",
        validators=[FLOAT_NUMBER_BRACKETS_FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    seven_six = models.CharField(
        max_length=256, verbose_name="навчальний посібник за кордоном", default="0",
        validators=[FLOAT_NUMBER_BRACKETS_FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 8 Виконання обов’язків гаранта ОП І освітнього рівня/ІІ ОР/ІІІ ОР
    eight_one = models.CharField(
        max_length=32, verbose_name="", choices=LEVELS_CHOICES, default=NONE, null=True, blank=True)

    # 9 Розробка НМКД
    nine_one = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[NUMBER_SEMICOLON_VALIDATOR])
    nine_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[NUMBER_SEMICOLON_VALIDATOR])

    # 10 Розробка нових
    ten_one = models.CharField(
        max_length=256, verbose_name="навчальних планів", default="0", validators=[NUMBER_SEMICOLON_VALIDATOR])
    ten_two = models.CharField(
        max_length=256, verbose_name="робочих навчальних планів", default="0", validators=[NUMBER_SEMICOLON_VALIDATOR])
    ten_three = models.CharField(
        max_length=256, verbose_name="навчальних планів", default="0", validators=[NUMBER_SEMICOLON_VALIDATOR])
    ten_four = models.CharField(
        max_length=256, verbose_name="робочих навчальних планів", default="0", validators=[NUMBER_SEMICOLON_VALIDATOR])

    # 11 Розробка і підготовка нових лабораторних робіт на лабораторному устаткуванні
    eleven_one = models.CharField(
        max_length=256, verbose_name="розробка і підготовка", default="0",
        validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    eleven_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 12 Розробка та затвердження нової освітньої (освітньо-професійної або освітньо-наукової) програми
    twelve_one = models.CharField(
        max_length=256, verbose_name="розробка та затвердження", default="0",
        validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 13 Підготовка справи та успішне проходження експертизи
    thirteen_one = models.CharField(
        max_length=256, verbose_name="ліцензійної", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    thirteen_two = models.CharField(
        max_length=256, verbose_name="акредитаційної", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 14 Підготовка комп’ютерного програмного забезпечення навчальних дисциплін
    fourteen_one = models.CharField(
        max_length=256, verbose_name="підготовка", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    fourteen_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 15 Розробка складових ЕОР
    fifteen_one = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    fifteen_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 16 Розробка програм і завдань до вступних випробувань
    sixteen_one = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    sixteen_two = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    sixteen_three = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    sixteen_four = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    sixteen_five = models.CharField(
        max_length=256, verbose_name="розробка", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])
    sixteen_six = models.CharField(
        max_length=256, verbose_name="оновлення", default="0", validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 17 Розробка і впровадження нових форм, методів і технологій навчання
    seventeen_one = models.CharField(
        max_length=256, verbose_name="розробка і впровадження", default="0",
        validators=[FLOAT_NUMBER_SEMICOLON_VALIDATOR])

    # 18 Підготовка концертних програм і персональних художніх виставок, спортивних заходів
    eighteen_one = models.IntegerField(default=0)

    # 19 Отримання звання
    nineteen_one = models.CharField(max_length=30, choices=POSITION_CHOICES, default=NONE, null=True, blank=True)

    @staticmethod
    def get_report(user, report_period: ReportPeriod):
        return EducationalAndMethodicalWork.objects.filter(
            generic_report_data__user=user, generic_report_data__report_period=report_period).first()

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
        verbose_name="Загальне значення", default=0, validators=[validators.MinValueValidator(0)])

    @staticmethod
    def get_report(user, report_period: ReportPeriod):
        return ScientificAndInnovativeWork.objects.filter(
            generic_report_data__user=user, generic_report_data__report_period=report_period).first()

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
        max_length=10, verbose_name="посада", default=NONE, choices=POSITION_CHOICES, blank=True, null=True)

    # 2. Робота в Акредитаційній комісії або її експертних рад, галузевих експертних радах НАЗЯВО, або Міжгалузевої
    # експертної ради з вищої освіти Акредитаційної комісії, експертних комісіях МОН/зазначеного агентства
    two_one = models.BooleanField(default=False)

    # 3. Робота в експертних комісіях АКУ та ліцензування МОН
    three_one = models.BooleanField(default=False)

    # 4. Робота в науково-технічній раді НДЧ ДНУ, науково-методичній раді, РЗЯВО, БЗЯВО університету (факультету)
    four_one = models.CharField(
        verbose_name="Робота в науково-технічній раді НДЧ ДНУ", max_length=10, choices=POSITION_CHOICES, default=NONE,
        blank=True, null=True)
    four_two = models.CharField(
        verbose_name="Робота в науково-методичній раді", max_length=10, choices=POSITION_CHOICES, default=NONE,
        blank=True, null=True)
    four_three = models.CharField(
        verbose_name="Робота в науково-методичній раді", max_length=10, choices=POSITION_CHOICES, default=NONE,
        blank=True, null=True)
    four_four = models.CharField(
        verbose_name="Робота в раді та бюро із забезпечення якості вищої освіти (РЗЯВО, БЗЯВО)",
        max_length=10, choices=POSITION_CHOICES, default=NONE, blank=True, null=True)
    four_five = models.CharField(
        verbose_name="Робота в раді та бюро із забезпечення якості вищої освіти (РЗЯВО, БЗЯВО)",
        max_length=10, choices=POSITION_CHOICES, default=NONE, blank=True, null=True)
    four_six = models.CharField(
        verbose_name="Робота у бюро з академічної доброчесності факультету", max_length=10,
        choices=POSITION_CHOICES, default=NONE, blank=True, null=True)

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
    eleven_one = models.BooleanField(
        verbose_name="виконання обов’язків куратора (наставника) академічної групи", default=False)
    eleven_two = models.BooleanField(verbose_name="проведення виховної роботи в гуртожитках", default=False)

    # 12. Робота у складі вченої ради ДНУ
    twelve_one = models.BooleanField(default=False)

    # 13. Робота у складі вченої ради факультету
    thirteen_one = models.CharField(
        verbose_name="Робота у складі вченої ради факультету", choices=POSITION_CHOICES, default=NONE,
        blank=True, null=True, max_length=10)

    # 14. Організаційна робота
    fourteen_one = models.BooleanField(
        verbose_name="завідувача кафедри (у тому числі відвідування занять завідувачем кафедри зі складанням відгуку, "
                     "проведення засідань кафедри, участь у засіданнях  деканату факультету)", default=False)
    fourteen_two = models.BooleanField(
        verbose_name="заступник завідувача кафедри на громадських засадах", default=False)

    # 15. Взаємовідвідування занять НПП (крім завідувача кафедри) зі складанням відгуку в журналі взаємовідвідувань
    fifteen_one = models.IntegerField(verbose_name="кількість відвіданих занять", default=0)

    # 16. Участь у профорієнтаційній роботі кафедри, факультету, університету
    sixteen_one = models.IntegerField(verbose_name="кількість заходів", default=0)

    # 17. Робота в приймальній комісії (відповідно до наказів)
    seventeen_one = models.BooleanField(verbose_name="відповідальний секретар", default=False)
    seventeen_two = models.BooleanField(verbose_name="заступник відповідального секретаря", default=False)
    seventeen_three = models.BooleanField(
        verbose_name="голова предметної екзаменаційної комісії, комісії зі співбесіди", default=False)
    seventeen_four = models.IntegerField(verbose_name="робота у відбірковій комісії", default=0)
    seventeen_five = models.IntegerField(
        verbose_name="член комісії зі співбесіді, предметної екзаменаційної комісії", default=0)
    seventeen_six = models.IntegerField(
        verbose_name="робота у групі контролю й введення даних до ЄДЕБО (відповідальний за введення даних до ЄДЕБО)",
        default=0)
    seventeen_seven = models.IntegerField(
        verbose_name="робота у складі асистентської групи приймальної комісії", default=0)
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

    @staticmethod
    def get_report(user, report_period):
        return OrganizationalAndEducationalWork.objects.filter(
            generic_report_data__user=user, generic_report_data__report_period__report_period=report_period).first()

    @staticmethod
    def slug():
        return "organizational_and_educational_work"

    def __str__(self):
        return self.NAME

    class Meta:
        verbose_name = 'Звіт "Організаційно-виховна робота"'
        verbose_name_plural = 'Звіти "Організаційно-виховна робота"'


REPORT_MODELS = (
    EducationalAndMethodicalWork,
    ScientificAndInnovativeWork,
    OrganizationalAndEducationalWork
)
# Generated by Django 3.2.4 on 2021-07-12 11:37

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_api', '0007_auto_20210702_1109'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='educationalandmethodicalwork',
            name='eight_three',
        ),
        migrations.RemoveField(
            model_name='educationalandmethodicalwork',
            name='eight_two',
        ),
        migrations.RemoveField(
            model_name='educationalandmethodicalwork',
            name='one_four',
        ),
        migrations.RemoveField(
            model_name='genericreportdata',
            name='additional_assignment',
        ),
        migrations.RemoveField(
            model_name='genericreportdata',
            name='main_assignment',
        ),
        migrations.AddField(
            model_name='educationalandmethodicalwork',
            name='six_two',
            field=models.IntegerField(default=0, help_text='Кількість участників проєкту', verbose_name='В ролі виконавця'),
        ),
        migrations.AddField(
            model_name='genericreportdata',
            name='assignment',
            field=models.FloatField(default=1, help_text='Значення від 0 до 1', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], verbose_name='Доля ставки, яку обіймає за основною посадою або за штатним сумісництвом'),
        ),
        migrations.AddField(
            model_name='reportperiod',
            name='annual_workload',
            field=models.FloatField(default=0, validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(600)], verbose_name='середньорічне навчальне навантаження в ДНУ (год.)'),
        ),
        migrations.AlterField(
            model_name='educationalandmethodicalwork',
            name='eight_one',
            field=models.CharField(blank=True, choices=[(None, '-'), ('І освітній рівень', 'І освітній рівень'), ('ІІ освітній рівень', 'ІІ освітній рівень'), ('ІІІ освітній рівень', 'ІІІ освітній рівень')], default=None, max_length=32, null=True, verbose_name=''),
        ),
        migrations.AlterField(
            model_name='educationalandmethodicalwork',
            name='one_one',
            field=models.FloatField(default=0, help_text='До аудиторного навантаження включаються години за проведення лекційних, практичних, семінарських, лабораторних занять.', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(600)], verbose_name='обсяг виконаного аудиторного навантаження (год.)'),
        ),
        migrations.AlterField(
            model_name='educationalandmethodicalwork',
            name='six_one',
            field=models.BooleanField(default=False, verbose_name='В ролі керівника'),
        ),
        migrations.AlterField(
            model_name='educationalandmethodicalwork',
            name='three_two',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0)], verbose_name='конкурсних дипломних проєктів і робіт'),
        ),
        migrations.AlterField(
            model_name='genericreportdata',
            name='assignment_duration',
            field=models.FloatField(default=10, help_text='Значення від 0 до 10', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(10)], verbose_name='Кількість відпрацьованих місяців за звітний період'),
        ),
        migrations.AlterField(
            model_name='genericreportdata',
            name='students_rating',
            field=models.FloatField(default=0, help_text='Значення від 0 до 200 балів. Сума балів, які отримані НПП за результатами двох анкетувань (1 та 2 семестр)', validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(200)], verbose_name='Бал за наслідками анонімного анкетування студентів'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='fifteen_one',
            field=models.IntegerField(default=0, verbose_name='кількість занять відвідувань занять'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='five_three',
            field=models.IntegerField(default=0, verbose_name='член оргкомітету'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='four_five',
            field=models.CharField(blank=True, choices=[(None, '-'), ('head', 'голова, заступник голови'), ('secretary', 'секретар'), ('member', 'член комісії')], default=None, max_length=10, null=True, verbose_name='Робота в раді та бюро із забезпечення якості вищої освіти (РЗЯВО, БЗЯВО)'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='four_four',
            field=models.CharField(blank=True, choices=[(None, '-'), ('head', 'голова, заступник голови'), ('secretary', 'секретар'), ('member', 'член комісії')], default=None, max_length=10, null=True, verbose_name='Робота в раді та бюро із забезпечення якості вищої освіти (РЗЯВО, БЗЯВО)'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='four_one',
            field=models.CharField(blank=True, choices=[(None, '-'), ('head', 'голова, заступник голови'), ('secretary', 'секретар'), ('member', 'член комісії')], default=None, max_length=10, null=True, verbose_name='Робота в науково-технічній раді НДЧ ДНУ'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='four_six',
            field=models.CharField(blank=True, choices=[(None, '-'), ('head', 'голова, заступник голови'), ('secretary', 'секретар'), ('member', 'член комісії')], default=None, max_length=10, null=True, verbose_name='Робота у бюро з академічної доброчесності факультету'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='four_three',
            field=models.CharField(blank=True, choices=[(None, '-'), ('head', 'голова, заступник голови'), ('secretary', 'секретар'), ('member', 'член комісії')], default=None, max_length=10, null=True, verbose_name='Робота в науково-методичній раді'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='four_two',
            field=models.CharField(blank=True, choices=[(None, '-'), ('head', 'голова, заступник голови'), ('secretary', 'секретар'), ('member', 'член комісії')], default=None, max_length=10, null=True, verbose_name='Робота в науково-методичній раді'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='six_one',
            field=models.BooleanField(default=False, verbose_name='навчальна робота'),
        ),
        migrations.AlterField(
            model_name='organizationalandeducationalwork',
            name='ten_one',
            field=models.IntegerField(default=0, verbose_name='кількість студентів, яким замовлено додатки'),
        ),
    ]

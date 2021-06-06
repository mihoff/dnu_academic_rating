# Generated by Django 3.2.4 on 2021-06-06 19:35

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_api', '0002_auto_20210606_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='educationalandmethodicalwork',
            name='eight_one',
            field=models.IntegerField(default=0, validators=[django.core.validators.RegexValidator('^[\\d+\\s*]+$', message='Невірний формат даних. Введіть числа через пробіл.')], verbose_name='І освітній рівень'),
        ),
        migrations.AlterField(
            model_name='educationalandmethodicalwork',
            name='eight_three',
            field=models.IntegerField(default=0, validators=[django.core.validators.RegexValidator('^[\\d+\\s*]+$', message='Невірний формат даних. Введіть числа через пробіл.')], verbose_name='ІІІ освітній рівень'),
        ),
        migrations.AlterField(
            model_name='educationalandmethodicalwork',
            name='eight_two',
            field=models.IntegerField(default=0, validators=[django.core.validators.RegexValidator('^[\\d+\\s*]+$', message='Невірний формат даних. Введіть числа через пробіл.')], verbose_name='ІІ освітній рівень'),
        ),
    ]

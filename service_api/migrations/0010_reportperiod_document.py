# Generated by Django 3.2.4 on 2021-08-31 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('service_api', '0009_auto_20210712_1507'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportperiod',
            name='document',
            field=models.FileField(default=None, null=True, upload_to='', verbose_name='Положення'),
        ),
    ]

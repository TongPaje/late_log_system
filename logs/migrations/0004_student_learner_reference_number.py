# Generated by Django 5.2.1 on 2025-05-23 06:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('logs', '0003_alter_student_section'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='learner_reference_number',
            field=models.CharField(default=123424, max_length=100, unique=True),
            preserve_default=False,
        ),
    ]

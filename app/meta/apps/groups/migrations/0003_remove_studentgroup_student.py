# Generated by Django 3.2.12 on 2022-11-03 19:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0002_studentgroup_student'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='studentgroup',
            name='student',
        ),
    ]
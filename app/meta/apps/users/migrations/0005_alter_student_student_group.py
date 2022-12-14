# Generated by Django 3.2.12 on 2022-11-04 14:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('groups', '0004_alter_studentgroup_title'),
        ('users', '0004_alter_student_student_group'),
    ]

    operations = [
        migrations.AlterField(
            model_name='student',
            name='student_group',
            field=models.ManyToManyField(blank=True, null=True, related_name='set_students', to='groups.StudentGroup'),
        ),
    ]

# Generated by Django 3.2.8 on 2022-07-11 18:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('students', '0008_alter_graduateswithprograms_unique_together'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='graduateswithprograms',
            options={
                'ordering':
                ('-passing_year', '-is_ug', 'under_campus', 'under_institute')
            },
        ),
    ]

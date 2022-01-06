# Generated by Django 3.2.8 on 2022-01-06 08:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organization', '0001_initial'),
        ('students', '0008_auto_20211028_1226'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='institute',
            name='under_campus',
        ),
        migrations.AlterField(
            model_name='graduates',
            name='under_campus',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.campus'),
        ),
        migrations.AlterField(
            model_name='graduates',
            name='under_institute',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='organization.institute'),
        ),
        migrations.DeleteModel(
            name='Campus',
        ),
        migrations.DeleteModel(
            name='Institute',
        ),
    ]

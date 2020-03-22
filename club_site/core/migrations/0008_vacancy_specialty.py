# Generated by Django 3.0.3 on 2020-03-22 12:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_vacancy'),
    ]

    operations = [
        migrations.AddField(
            model_name='vacancy',
            name='specialty',
            field=models.CharField(choices=[('Программист', 'Программист'), ('Маркетолог', 'Маркетолог'), ('Менеджер', 'Менеджер'), ('Дизайнер', 'Дизайнер')], default='Менеджер', max_length=25),
        ),
    ]

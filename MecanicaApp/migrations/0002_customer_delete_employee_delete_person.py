# Generated by Django 4.2.13 on 2024-06-13 17:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('MecanicaApp', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('vehicle', models.CharField(max_length=30)),
            ],
        ),
        migrations.DeleteModel(
            name='Employee',
        ),
        migrations.DeleteModel(
            name='Person',
        ),
    ]

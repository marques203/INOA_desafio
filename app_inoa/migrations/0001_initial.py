# Generated by Django 4.2.4 on 2023-09-16 16:10

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ativo",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("nome_ativo", models.TextField(max_length=10)),
                ("tunel_max", models.IntegerField()),
                ("tunel_min", models.IntegerField()),
                ("periodo", models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name="email",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("email", models.TextField(max_length=255)),
            ],
        ),
    ]

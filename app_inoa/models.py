from django.db import models

# Create your models here.
class Email(models.Model):
    email = models.TextField(max_length=255, null=True)

class Ativo(models.Model):
    nome_ativo = models.TextField(max_length=10)
    tunel_max = models.IntegerField()
    tunel_min = models.IntegerField()
    periodo = models.IntegerField()
    precos = models.JSONField(default=list)
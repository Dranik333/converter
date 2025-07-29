from django.db import models

class Currency(models.Model):
    name = models.CharField("Название валюты", max_length=50)
    code = models.CharField("Код валюты", max_length=3, unique=True)
    rate = models.DecimalField("Курс", max_digits=10, decimal_places=4)

    def __str__(self):
        return f"{self.name} ({self.code})"

# Create your models here.

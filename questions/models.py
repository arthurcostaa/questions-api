from django.db import models
from django.core.validators import MinValueValidator


class Question(models.Model):
    EDUCATION_LEVEL = (
        ('EF', 'ENSINO FUNDAMENTAL'),
        ('EM', 'ENSINO MÉDIO'),
        ('ES', 'ENSINO SUPERIOR'),
    )
    stem = models.TextField(max_length=2000)
    year = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1900)]
    )
    education_level = models.CharField(max_length=2, choices=EDUCATION_LEVEL)

    def __str__(self):
        return self.stem[:50]

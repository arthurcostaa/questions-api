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


class Choice(models.Model):
    DISPLAY_ORDER = (
        (1, 'a'),
        (2, 'b'),
        (3, 'c'),
        (4, 'd'),
        (5, 'e'),
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField()
    display_order = models.PositiveSmallIntegerField(choices=DISPLAY_ORDER)
    question = models.ForeignKey(
        Question,
        on_delete=models.PROTECT,
        related_name='choices'
    )

    class Meta:
        ordering = ['question', 'display_order']

    def __str__(self):
        return f'{self.display_order} - {self.question}'

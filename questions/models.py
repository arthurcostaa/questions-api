from django.conf import settings
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


class UserAnswer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.PROTECT)
    choice = models.ForeignKey(Choice, on_delete=models.PROTECT)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    answered_at = models.DateTimeField(auto_now=True)
    is_correct = models.BooleanField(blank=True, null=True)

    def __str__(self):
        return f'{self.user.name} - {self.question}'

    def save(self, **kwargs):
        correct_answer = self.question.choices.get(is_correct=True)
        self.is_correct = self.choice == correct_answer
        return super().save(**kwargs)

from django.contrib import admin

from questions.models import Question

class QuestionAdmin(admin.ModelAdmin):
    list_display = ['stem', 'year', 'education_level']


admin.site.register(Question, QuestionAdmin)

from django.contrib import admin

from questions.models import Choice, Question


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 0


class QuestionAdmin(admin.ModelAdmin):
    list_display = ['stem', 'year', 'education_level']
    inlines = [ChoiceInline]


class ChoiceAdmin(admin.ModelAdmin):
    list_display = ['question', 'text', 'is_correct', 'display_order']
    fields = ['question', 'text', 'display_order', 'is_correct']


admin.site.register(Question, QuestionAdmin)
admin.site.register(Choice, ChoiceAdmin)

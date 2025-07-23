from datetime import date

from rest_framework import serializers

from questions.models import Question


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['id', 'stem', 'year', 'education_level']

    def validate_year(self, value):
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError('Question year can not be in the future.')
        return value

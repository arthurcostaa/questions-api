from datetime import date

from rest_framework import serializers

from questions.models import Choice, Question


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'display_order']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'stem', 'year', 'education_level', 'choices']

    def validate_choices(self, value):
        MIN_CHOICES = 4
        MAX_CHOICES = 5

        if value is not None and len(value) > MAX_CHOICES or len(value) < MIN_CHOICES:
            raise serializers.ValidationError('A question should have 4 or 5 choices.')

        num_true_questions = sum(choice['is_correct'] for choice in value)
        if num_true_questions != 1:
            raise serializers.ValidationError('A question should have only one correct choice.')

        return value

    def validate_year(self, value):
        current_year = date.today().year
        if value > current_year:
            raise serializers.ValidationError('Question year can not be in the future.')
        return value

    def create(self, validated_data):
        choices = validated_data.pop('choices')
        question = Question.objects.create(**validated_data)

        for choice in choices:
            Choice.objects.create(question=question, **choice)

        return question

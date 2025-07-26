from datetime import date

from rest_framework import serializers

from questions.models import Choice, Question
from questions.utils import (
    has_only_one_correct_choice,
    has_unique_display_order,
    has_valid_number_of_choices,
)


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = ['id', 'text', 'is_correct', 'display_order']


class QuestionSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)

    class Meta:
        model = Question
        fields = ['id', 'stem', 'year', 'education_level', 'choices']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        request = self.context.get('request')

        if request is not None and not request.user.is_staff:
            for choice in representation['choices']:
                if 'is_correct' in choice:
                    choice.pop('is_correct')

        return representation

    def validate_choices(self, value):
        if not has_valid_number_of_choices(value):
            raise serializers.ValidationError('A question should have 4 or 5 choices.')

        if not has_only_one_correct_choice(value):
            raise serializers.ValidationError('A question should have only one correct choice.')

        if not has_unique_display_order(value):
            raise serializers.ValidationError(
                'A question cannot have choices with repeated display order.'
            )

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

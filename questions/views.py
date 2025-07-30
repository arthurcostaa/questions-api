from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from questions.models import Question
from questions.serializers import QuestionSerializer


class QuestionViewSet(viewsets.GenericViewSet):
    queryset = Question.objects.prefetch_related('choices').all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_permissions(self):
        if self.action in ('create', 'destroy', 'update'):
            return [permissions.IsAdminUser()]
        return super().get_permissions()

    def perform_destroy(self, instance):
        instance.choices.all().delete()
        instance.delete()

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def destroy(self, request, pk=None):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def update(self, request, pk=None):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

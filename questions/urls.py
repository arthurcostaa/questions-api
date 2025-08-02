from django.urls import include, path
from rest_framework_nested import routers

from . import views

router = routers.SimpleRouter()

router.register(r'questions', views.QuestionViewSet, basename='question')

questions_router = routers.NestedDefaultRouter(router, r'questions', lookup='question')
questions_router.register(r'answer', views.UserAnswerViewSet, basename='question-answer')

urlpatterns = [
    path(r'', include(router.urls)),
    path(r'', include(questions_router.urls)),
]
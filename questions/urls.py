from rest_framework import routers

from . import views

router = routers.SimpleRouter()
router.register(r'', views.QuestionViewSet, basename='questions')

urlpatterns = router.urls

from django.urls import path

from . import views

urlpatterns = [
    path('', views.CustomUserCreateView.as_view()),
    path('<int:pk>/', views.CustomUserRetrieveUpdateDestroyView.as_view()),
]

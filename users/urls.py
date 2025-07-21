from django.urls import path

from . import views

urlpatterns = [
    path('', views.CustomUserCreateView.as_view(), name='create'),
    path(
        '<int:pk>/',
        views.CustomUserRetrieveUpdateDestroyView.as_view(),
        name='retrieve-update-destroy'
    ),
]

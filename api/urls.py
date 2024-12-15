from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'environments', views.EnvironmentViewSet, basename='environment')

urlpatterns = [
    path('auth/', views.LoginView().as_view()),
    path('api/v1/', include(router.urls)),
]

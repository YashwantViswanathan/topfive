from django.urls import path
from . import views

urlpatterns = [
    path('', views.similarity_view, name='similarity'),
    path('api/similarity/', views.similarity_api_view, name='similarity_api'),
]

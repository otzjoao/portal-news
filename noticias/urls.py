from django.urls import path
from . import views

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('categoria/<slug:slug>/', views.PorCategoria.as_view(), name='categoria'),
    path('noticia/<slug:slug>/', views.Detalhe.as_view(), name='detalhe'),
]
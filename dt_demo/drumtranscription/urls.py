from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^index/', views.index, name='index'),
    url(r'^loading/calculate/', views.calculate, name='calculate'),
    url(r'^loading/', views.loading, name='loading'),
    url(r'^player/', views.player, name='player'),
]
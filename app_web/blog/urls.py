from django.urls import path
from . import views

urlpatterns= [
    path('',views.home,name="home")## cet fonction prend trois parametre qui sont le path ou encore chemin d'acces ,le nom de la view,et le nom qu'on met a l'url
]
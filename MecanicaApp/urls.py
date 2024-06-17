from django.urls import path

from . import views

# Aqui se agregan las URL, es decir las formas en que se van a llamar a lo que hacemos en viwes.py

urlpatterns = [
    path("", views.index, name="index"),
    path("register/", views.register, name="register"),
    path("qr/", views.qr_code_view, name="qr"),
    path("mostrarAutos/", views.mostrar_autos, name="mostrarAutos"),
    path("registrarAuto/",views.registrar_auto,name="registrarAuto")

]

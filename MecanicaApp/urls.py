from django.urls import path

from . import views

# Aqui se agregan las URL, es decir las formas en que se van a llamar a lo que hacemos en viwes.py

urlpatterns = [
    path("", views.index, name="index"),
    path("redirect/", views.default_view, name="default_view"),
    path("register/", views.register, name="register"),

    path('generate_qr/', views.qr_code_view, name='generate_qr'),
    path('login/', views.login, name='login'),
    path("mostrarAutos/", views.mostrar_autos, name="mostrarAutos"),
    path("registrarAuto/", views.registrar_auto, name="registrarAuto"),
    path("mostrarEstacion/", views.mostrar_estacion, name="mostrarEstacion"),
    path("enviarCorreo/",views.token_sended_test, name="enviarCorreo"),
    path("recuperarContraseña/",views.send_email_form, name="recuperarContraseña"),
    path("confirmarContrasenia/", views.password_confirmation, name="confirmarContrasenia"),
    path("registrarAuto/",views.registrar_auto,name="registrarAuto"),
    path('eliminarAuto/<int:auto_id>/', views.eliminar_auto, name='eliminarAuto'),
    path('logout/', views.logout_user, name='logout'),
    path("ordenarServicio/<str:id>/", views.ordenar_servicio, name="ordenarServicio"),
    path("ordenes/", views.listar_ordenes, name="listar_ordenes"),
    path('orden/<int:id>/', views.detalle_orden, name='detalle_orden'),

    # Para crear un admin base
    path('admin/create/', views.create_admin, name='create_admin'),

    # Lo de mis amiguitos
    path('payment/', views.payment, name='payment'),
    path('transferencia/', views.transferencia, name='transferencia'),
    path('retirarAuto/', views.retirarAuto, name='retirarAuto'),
    path('success/', views.success, name='success'),
    path('subirQR/', views.subirQR, name='subirQR'),
    path("registrarAuto/",views.registrar_auto,name="registrarAuto"),

    path("mostrarServicios/",views.mostrar_servicios, name='mostrarServicios'),

    path("crearServicio/", views.crearServicios, name="crearServicio"),

    path("editar_servicio/<str:service_name>/", views.editarServicios, name='editar_servicio'),


    path('admin/customers/', views.admin_customer_list, name='admin_customer_list'),

]

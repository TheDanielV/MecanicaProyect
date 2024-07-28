from django.urls import path

from . import views

# Aqui se agregan las URL, es decir las formas en que se van a llamar a lo que hacemos en viwes.py

urlpatterns = [
    path("", views.index, name="index"),
    path("redirect/", views.default_view, name="default_view"),
    # Autorizacion
    path("register/", views.register, name="register"),
    path('generate_qr/<str:order_id>/', views.qr_code_view, name='generate_qr'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout_user, name='logout'),
    # Cliente
    path("mostrarAutos/", views.mostrar_autos, name="mostrarAutos"),
    path("registrarAuto/", views.registrar_auto, name="registrarAuto"),
    path("mostrarEstacion/", views.mostrar_estacion, name="mostrarEstacion"),
    path("enviarCorreo/",views.token_sended_test, name="enviarCorreo"),
    path("recuperarContraseña/",views.send_email_form, name="recuperarContraseña"),
    path("confirmarContrasenia/", views.password_confirmation, name="confirmarContrasenia"),
    path("registrarAuto/",views.registrar_auto,name="registrarAuto"),
    path('eliminarAuto/<int:auto_id>/', views.eliminar_auto, name='eliminarAuto'),
    path('ordenesCliente/', views.orders, name="ordenes"),
    # Ordenes
    path("ordenarServicio/<str:id>/", views.ordenar_servicio, name="ordenarServicio"),
    path("generarOrden/", views.generate_order, name="generarOrden"),
    path("ordenes/", views.listar_ordenes, name="listar_ordenes"),
    path('orden/<int:id>/', views.detalle_orden, name='detalle_orden'),
    path('ordenCliente/<int:id>/', views.detalle_orden_cliente, name='detalle_orden_customer'),


    # para registrar un empleado
    path('registrarEmpleado/', views.agregar_empleado, name='registrarEmpleado'),
    # Para crear un admin base
    path('admin/create/', views.create_admin, name='create_admin'),

    # Lo de mis amiguitos
    path('payment/<int:id>/', views.payment, name='payment'),
    path('transferencia/<int:id>/', views.transferencia, name='transferencia'),
    path('retirarAuto/', views.retirarAuto, name='retirarAuto'),
    path('success/', views.success, name='success'),
    path('subirQR/', views.subirQR, name='subirQR'),
    path('actualizar/', views.update_state, name='actualizar_estado'),
    path("registrarAuto/", views.registrar_auto,name="registrarAuto"),

    # Servicios
    path("mostrarServicios/", views.mostrar_servicios, name='mostrarServicios'),
    path("crearServicio/", views.crearServicios, name="crearServicio"),
    path('deleteService/<int:id>/', views.delete_service, name='deleteService'),
    path("editar_servicio/<int:id>/", views.editarServicios, name='editar_servicio'),

    #payments
    path('Payment/<int:id>/', views.upload_payment, name='uploadPayment'),


    # path('admin/customers/', views.admin_customer_list, name='admin_customer_list'),

]

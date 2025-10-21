from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # Administración
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-panel/', views.admin_panel, name='admin_panel'),

    # Productos
    path('gestionar-productos/', views.gestionar_productos, name='gestionar_productos'),
    path('gestionar-productos/eliminar/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),

    # Categorías
    path('gestionar-categorias/', views.gestionar_categorias, name='gestionar_categorias'),
    path('gestionar-categorias/eliminar/<int:categoria_id>/', views.eliminar_categoria, name='eliminar_categoria'),

    # Usuarios
    path('gestionar-usuarios/', views.gestionar_usuarios, name='gestionar_usuarios'),
    path('gestionar-usuarios/eliminar/<int:usuario_id>/', views.eliminar_usuario, name='eliminar_usuario'),

    # Tienda
    path('categoria/<int:categoria_id>/', views.productos_por_categoria, name='productos_por_categoria'),
    path('carrito/', views.ver_carrito, name='ver_carrito'),
    path('agregar-carrito/<int:producto_id>/', views.agregar_carrito, name='agregar_carrito'),
    path('eliminar-carrito/<int:producto_id>/', views.eliminar_carrito, name='eliminar_carrito'),
   
    path('actualizar-stock/<int:producto_id>/', views.actualizar_stock, name='actualizar_stock'),
    
    path('datos-compra/', views.datos_compra, name='datos_compra'),
    path('finalizar-compra/', views.finalizar_compra, name='finalizar_compra'),
    path('factura/<int:pedido_id>/', views.generar_factura_pdf, name='generar_factura_pdf'),
]

from django.shortcuts import render, redirect,get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login
from .models import Categoria, Producto, Usuario,DetallePedido,Cliente,Pedido
from django.contrib import messages
from django.http import JsonResponse
from .forms import DatosCompraForm
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from django.http import HttpResponse
from decimal import Decimal

# ---------------------------
# HOME
# ---------------------------
def home(request):
    categorias = Categoria.objects.all()
    return render(request, 'home.html', {'categorias': categorias})

# ---------------------------
# LOGIN ADMIN
# ---------------------------
def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('admin_panel')
        else:
            return render(request, 'admin_login.html', {'error': 'Usuario o contraseña incorrecta'})
    return render(request, 'admin_login.html')

# ---------------------------
# PANEL ADMIN
# ---------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def admin_panel(request):
    return render(request, 'admin_panel.html')

# ---------------------------
# GESTIONAR PRODUCTOS
# ---------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestionar_productos(request):
    categorias = Categoria.objects.all()

    if request.method == "POST":
        producto_id = request.POST.get('producto_id')  # Para modificación
        nombre = request.POST.get('nombre')
        descripcion = request.POST.get('descripcion')
        precio = request.POST.get('precio')
        stock = request.POST.get('stock')
        categoria_id = request.POST.get('categoria')
        imagen = request.FILES.get('imagen')
        activo = request.POST.get('activo') == 'on'

        categoria = Categoria.objects.get(id=categoria_id)

        if producto_id:  # Modificación
            producto = Producto.objects.get(id=producto_id)
            producto.nombre = nombre
            producto.descripcion = descripcion
            producto.precio = precio
            producto.stock = stock
            producto.categoria = categoria
            producto.imagen = imagen or producto.imagen
            producto.activo = activo
            producto.save()
        else:  # Creación
            Producto.objects.create(
                nombre=nombre,
                descripcion=descripcion,
                precio=precio,
                stock=stock,
                categoria=categoria,
                imagen_url=imagen,
                activo=activo
            )
        return redirect('gestionar_productos')

    productos = Producto.objects.all()
    return render(request, 'gestionar_productos.html', {
        'productos': productos,
        'categorias': categorias
    })

# ---------------------------
# ELIMINAR PRODUCTO
# ---------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_producto(request, producto_id):
    try:
        producto = Producto.objects.get(id=producto_id)
        producto.delete()
    except Producto.DoesNotExist:
        pass
    return redirect('gestionar_productos')

# ---------------------------
# GESTIONAR CATEGORÍAS
# ---------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestionar_categorias(request):
    if request.method == "POST":
        categoria_id = request.POST.get('categoria_id')
        nombre = request.POST.get('nombre_categoria')
        descripcion = request.POST.get('descripcion')

        if categoria_id:  # Modificación
            categoria = Categoria.objects.get(id=categoria_id)
            categoria.nombre_categoria = nombre
            categoria.descripcion = descripcion
            categoria.save()
        else:  # Creación
            Categoria.objects.create(
                nombre_categoria=nombre,
                descripcion=descripcion
            )
        return redirect('gestionar_categorias')

    categorias = Categoria.objects.all()
    return render(request, 'gestionar_categorias.html', {'categorias': categorias})


# ---------------------------
# ELIMINAR CATEGORÍA
# ---------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_categoria(request, categoria_id):
    try:
        categoria = Categoria.objects.get(id=categoria_id)
        categoria.delete()
    except Categoria.DoesNotExist:
        pass
    return redirect('gestionar_categorias')


# ---------------------------
# GESTIONAR USUARIOS
# ---------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def gestionar_usuarios(request):
    usuarios = Usuario.objects.all()

    if request.method == "POST":
        id_usuario = request.POST.get("id_usuario")
        username = request.POST.get("username")
        email = request.POST.get("email")
        rol = request.POST.get("rol")
        password = request.POST.get("password")

        if id_usuario:  # Modificar usuario existente
            usuario = get_object_or_404(Usuario, id=id_usuario)
            usuario.username = username
            usuario.email = email
            usuario.rol = rol

            # Solo actualizar contraseña si se proporcionó y si es admin
            if rol == "admin" and password:
                usuario.set_password(password)
            usuario.save()
            messages.success(request, "Usuario modificado exitosamente.")
        else:  # Crear nuevo usuario
            if rol == "admin":
                if not password:
                    messages.error(request, "El administrador debe tener una contraseña.")
                else:
                    usuario = Usuario(username=username, email=email, rol=rol)
                    usuario.set_password(password)
                    usuario.save()
                    messages.success(request, "Administrador creado exitosamente.")
            else:  # Cliente
                usuario = Usuario.objects.create(username=username, email=email, rol=rol)
                usuario.set_unusable_password()  # No requiere contraseña
                usuario.save()
                messages.success(request, "Cliente creado exitosamente.")

        return redirect("gestionar_usuarios")

    return render(request, "gestionar_usuarios.html", {"usuarios": usuarios})

# ---------------------------
# ELIMINAR USUARIO
# ---------------------------
@login_required
@user_passes_test(lambda u: u.is_superuser)
def eliminar_usuario(request, usuario_id):
    try:
        usuario = Usuario.objects.get(id=usuario_id)
        usuario.delete()
    except Usuario.DoesNotExist:
        pass
    return redirect('gestionar_usuarios')

# ---------------------------
# PRODUCTOS POR CATEGORÍA
# ---------------------------
def productos_por_categoria(request, categoria_id):
    categoria = get_object_or_404(Categoria, id=categoria_id)
    productos = Producto.objects.filter(categoria=categoria, activo=True)
    return render(request, 'productos_categoria.html', {
        'categoria': categoria,
        'productos': productos
    })

# ---------------------------
# AGREGAR AL CARRITO
# ---------------------------

def agregar_carrito(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    cantidad = int(request.POST.get('cantidad', 1))

    if cantidad < 1:
        messages.warning(request, "La cantidad debe ser al menos 1.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    if cantidad > producto.stock:
        messages.warning(request, f"Solo hay {producto.stock} unidades disponibles.")
        return redirect(request.META.get('HTTP_REFERER', 'home'))

    carrito = request.session.get('carrito', {})

    if str(producto_id) in carrito:
        nueva_cantidad = carrito[str(producto_id)]['cantidad'] + cantidad
        if nueva_cantidad > producto.stock:
            messages.warning(request, f"No puedes agregar más de {producto.stock} unidades en total.")
        else:
            carrito[str(producto_id)]['cantidad'] = nueva_cantidad
            messages.success(request, f"Se agregaron {cantidad} unidades más de {producto.nombre}.")
    else:
        carrito[str(producto_id)] = {
            'nombre': producto.nombre,
            'precio': float(producto.precio),
            'cantidad': cantidad,
            'imagen': producto.imagen.url if producto.imagen else ''
        }
        messages.success(request, f"{producto.nombre} se agregó al carrito ({cantidad} unidades).")

    request.session['carrito'] = carrito
    return redirect(request.META.get('HTTP_REFERER', 'home'))
# ---------------------------
# VER CARRITO
# ---------------------------
def ver_carrito(request):
    carrito = request.session.get('carrito', {})
    total = Decimal('0.00')
    for item in carrito.values():
        item['subtotal'] = Decimal(item['precio']) * item['cantidad']
        total += item['subtotal']
    return render(request, 'carrito.html', {'carrito': carrito, 'total': total})


# FORMULARIO DE DATOS DE COMPRA (TEMPORAL)
def datos_compra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('ver_carrito')

    total = sum(Decimal(item['precio']) * item['cantidad'] for item in carrito.values())

    if request.method == 'POST':
        form = DatosCompraForm(request.POST)
        if form.is_valid():
            # Guardamos los datos en sesión temporalmente
            request.session['datos_compra'] = form.cleaned_data
            return redirect('finalizar_compra')
    else:
        form = DatosCompraForm()

    return render(request, 'datos_compra.html', {'form': form, 'total': total})

# FINALIZAR COMPRA Y MOSTRAR FACTURA
def finalizar_compra(request):
    carrito = request.session.get('carrito', {})
    if not carrito:
        messages.warning(request, "Tu carrito está vacío.")
        return redirect('ver_carrito')

    datos_compra = request.session.get('datos_compra')
    if not datos_compra:
        messages.warning(request, "Debes completar tus datos de compra.")
        return redirect('datos_compra')

    total = sum(Decimal(item['precio']) * item['cantidad'] for item in carrito.values())

    # Crear pedido sin asociarlo a un Cliente real
    pedido = Pedido.objects.create(
        total=total,
        estado='pendiente'
    )

    detalles = []
    for producto_id, item in carrito.items():
        producto = get_object_or_404(Producto, id=producto_id)
        cantidad = item['cantidad']

        if cantidad > producto.stock:
            messages.warning(request, f"No hay suficiente stock de {producto.nombre}.")
            pedido.delete()
            return redirect('ver_carrito')

        detalle = DetallePedido.objects.create(
            pedido=pedido,
            producto=producto,
            cantidad=cantidad,
            subtotal=Decimal(item['precio']) * cantidad
        )
        detalles.append(detalle)
        producto.stock -= cantidad
        producto.save()

    # Limpiar sesión
    request.session['carrito'] = {}
    request.session['datos_compra'] = {}

    return render(request, 'confirmacion_compra.html', {
        'pedido': pedido,
        'detalles': detalles,
        'nombre': datos_compra.get('nombre', ''),
        'apellido': datos_compra.get('apellido', ''),
        'direccion': datos_compra.get('direccion', ''),
        'telefono': datos_compra.get('telefono', ''),
        'total': total
    })
# ---------------------------
# ELIMINAR PRODUCTO DEL CARRITO
# ---------------------------
def eliminar_carrito(request, producto_id):
    carrito = request.session.get('carrito', {})
    if str(producto_id) in carrito:
        del carrito[str(producto_id)]
        request.session['carrito'] = carrito
        messages.success(request, "Producto eliminado del carrito.")
    return redirect('ver_carrito')



def actualizar_stock(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    carrito = request.session.get('carrito', {})
    cantidad_en_carrito = carrito.get(str(producto_id), {}).get('cantidad', 0)
    stock_disponible = producto.stock - cantidad_en_carrito
    return JsonResponse({'stock': stock_disponible})

def generar_factura_pdf(request, pedido_id):
    pedido = Pedido.objects.get(id=pedido_id)
    detalles = DetallePedido.objects.filter(pedido=pedido)

    # Crear la respuesta HTTP con tipo PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="factura_{pedido_id}.pdf"'

    # Crear el lienzo PDF
    p = canvas.Canvas(response, pagesize=letter)
    width, height = letter

    # Encabezado de la factura
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 770, "FACTURA DE COMPRA")

    # Información del pedido
    p.setFont("Helvetica", 12)
    p.drawString(100, 740, f"Número de pedido: {pedido.id}")

    # Manejar cliente anónimo
    if pedido.cliente:
        cliente_info = f"{pedido.cliente.nombre} {pedido.cliente.apellido}"
        direccion = pedido.cliente.direccion or "Sin dirección"
        telefono = pedido.cliente.telefono or "Sin teléfono"
    else:
        cliente_info = "Cliente anónimo"
        direccion = "No especificada"
        telefono = "No especificado"

    p.drawString(100, 720, f"Cliente: {cliente_info}")
    p.drawString(100, 705, f"Dirección: {direccion}")
    p.drawString(100, 690, f"Teléfono: {telefono}")

    p.drawString(100, 670, f"Fecha del pedido: {pedido.fecha_pedido.strftime('%d/%m/%Y')}")
    p.drawString(100, 655, f"Total: Q{pedido.total:.2f}")

    # Título de la tabla de productos
    p.setFont("Helvetica-Bold", 12)
    p.drawString(100, 630, "Producto")
    p.drawString(300, 630, "Cantidad")
    p.drawString(400, 630, "Subtotal (Q)")

    # Listar los productos del pedido
    y = 610
    p.setFont("Helvetica", 12)
    for detalle in detalles:
        p.drawString(100, y, detalle.producto.nombre)
        p.drawString(310, y, str(detalle.cantidad))
        p.drawString(410, y, f"{detalle.subtotal:.2f}")
        y -= 20

        # Salto de página si se llena
        if y < 100:
            p.showPage()
            y = 750
            p.setFont("Helvetica", 12)

    # Pie de página
    p.setFont("Helvetica-Oblique", 10)
    p.drawString(100, 80, "Gracias por su compra. ¡Vuelva pronto!")

    # Finalizar el PDF
    p.showPage()
    p.save()

    return response

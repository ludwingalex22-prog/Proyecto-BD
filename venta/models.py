from django.db import models

from django.contrib.auth.models import AbstractUser

# -------------------------------
# MODELO DE USUARIO PERSONALIZADO
# -------------------------------
class Usuario(AbstractUser):
    ROLES = (
        ('admin', 'Administrador'),
        ('cliente', 'Cliente'),
    )
    rol = models.CharField(max_length=10, choices=ROLES, default='cliente')

    def __str__(self):
        return f"{self.username} ({self.rol})"


# -------------------------------
# MODELO CATEGORÍA
# -------------------------------
class Categoria(models.Model):
    nombre_categoria = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.nombre_categoria


# -------------------------------
# MODELO PRODUCTO
# -------------------------------
class Producto(models.Model):
    nombre = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True, null=True)
    precio = models.DecimalField(max_digits=10, decimal_places=2)
    imagen = models.ImageField(upload_to='productos/', blank=True, null=True)
    stock = models.PositiveIntegerField(default=0)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='productos')
    activo = models.BooleanField(default=True)
    fecha_agregado = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nombre} (${self.precio})"


# -------------------------------
# MODELO CLIENTE
# -------------------------------
class Cliente(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='cliente')
    direccion = models.CharField(max_length=200, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.usuario.username


# -------------------------------
# MODELO PEDIDO
# -------------------------------
class Pedido(models.Model):
    ESTADOS = (
        ('pendiente', 'Pendiente'),
        ('pagado', 'Pagado'),
        ('enviado', 'Enviado'),
        ('cancelado', 'Cancelado'),
    )
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, related_name='pedidos', null=True, blank=True)
    fecha_pedido = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADOS, default='pendiente')

    def __str__(self):
        return f"Pedido #{self.id} - {self.cliente.usuario.username}"


# -------------------------------
# MODELO DETALLE DEL PEDIDO
# -------------------------------
class DetallePedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField(default=1)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad}"

    def save(self, *args, **kwargs):
        # Calcula subtotal automáticamente
        self.subtotal = self.producto.precio * self.cantidad
        super().save(*args, **kwargs)
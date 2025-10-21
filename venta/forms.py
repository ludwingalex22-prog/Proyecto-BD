from django import forms
from .models import Pedido, Cliente

class DatosCompraForm(forms.Form):
    nombre = forms.CharField(max_length=100)
    apellido = forms.CharField(max_length=100)
    direccion = forms.CharField(max_length=200)
    telefono = forms.CharField(max_length=20)
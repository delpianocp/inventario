from django.shortcuts import render, redirect, get_object_or_404
from .models import Articulo
from .forms import ArticuloForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .forms import RegistroForm
from django.contrib.auth import authenticate, login
from .forms import LoginForm
from django.contrib.auth import logout
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
import time
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.views import LoginView


def index(request):
    if request.method == "POST":
        form = LoginForm(data=request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            password = form.cleaned_data["password"]

            user = User.objects.filter(email=email).first()  # Buscar usuario por email
            if user:
                user = authenticate(username=user.username, password=password)

            if user:
                login(request, user)
                return redirect("articulos")
            else:
                form.add_error(None, "Correo o contraseña incorrectos.")

    else:
        form = LoginForm()
    
    return render(request, "inventario/index.html", {"form": form, "show_register": True, "show_inicio": False})



def registro(request):
    if request.method == "POST":
        form = RegistroForm(request.POST)
        if form.is_valid():
            usuario = form.save(commit=False)
            usuario.set_password(form.cleaned_data["password"])  # Encripta la contraseña
            usuario.save()
            return redirect("redirigiendo")

 # Redirige al login tras el registro
    else:
        form = RegistroForm()

    return render(request, "inventario/registro.html", {"form": form, "show_register": False, "show_inicio": True})

def redirigiendo(request):
    if request.user.is_authenticated:  # Verificamos si hay un usuario autenticado
        subject = "¡Registro exitoso!"
        message = f"Hola {request.user.username},\n\n¡Tu registro ha sido exitoso! Bienvenido."
        recipient_email = request.user.email
        send_mail(subject, message, settings.EMAIL_HOST_USER, [recipient_email])
    
    return render(request, "inventario/redirigiendo.html")
    


@login_required
def listar_articulos(request):
    articulos = Articulo.objects.all()  # Obtiene todos los artículos de la base de datos
    return render(request, "inventario/articulos.html", {"articulos": articulos})

@login_required
def cargar_articulo(request):
    if request.method == "POST":
        form = ArticuloForm(request.POST, request.FILES)
        if form.is_valid():
            articulo = form.save(commit=False)  # No guardamos todavía
            articulo.usuario = request.user  # Asignamos el usuario autenticado
            articulo.save()  # Ahora sí guardamos
            return redirect("articulos")
    else:
        form = ArticuloForm()

    return render(request, "inventario/cargar_articulo.html", {"form": form, "show_register": False, "show_inicio": False})

@login_required
def logout_view(request):
    logout(request)
    return redirect("index")

@login_required
def detalle_articulo(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)
    return render(request, "inventario/detalle_articulo.html", {"articulo": articulo})

@login_required
def editar_articulo(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)
    if request.method == "POST":
        form = ArticuloForm(request.POST, request.FILES, instance=articulo)
        if form.is_valid():
            form.save()
            return redirect("detalle_articulo", articulo_id=articulo.id)
    else:
        form = ArticuloForm(instance=articulo)

    return render(request, "inventario/editar_articulo.html", {"form": form, "articulo": articulo})

@login_required
def eliminar_articulo(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)
    if request.method == "POST":
        articulo.delete()
        return redirect("articulos")

    return render(request, "inventario/eliminar_articulo.html", {"articulo": articulo})

def truncar_texto(texto, longitud_maxima):
    """Trunca el texto si supera la longitud máxima"""
    return texto[:longitud_maxima] + "…" if len(texto) > longitud_maxima else texto

def generar_pdf(request):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "attachment; filename=lista_articulos.pdf"

    # Crear PDF con tamaño carta
    p = canvas.Canvas(response, pagesize=letter)
    p.setTitle("Lista de Artículos")

    # Encabezado
    p.setFont("Helvetica-Bold", 16)
    p.drawString(200, 750, "Lista de Artículos")

    # Datos para la tabla
    data = [["ID", "Nombre", "Cantidad", "Asignación", "Valor"]]  # Encabezados
    articulos = Articulo.objects.all()

    for articulo in articulos:
        data.append([
            articulo.id, 
            truncar_texto(articulo.nombre, 20),  # Limita el nombre a 20 caracteres
            articulo.cantidad, 
            truncar_texto(articulo.asignacion, 15),  # Limita asignación a 15 caracteres
            f"${articulo.valor}"
        ])

    # Crear tabla con columnas bien definidas
    table = Table(data, colWidths=[50, 150, 80, 120, 80])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
    ]))

    # Posicionar tabla
    table.wrapOn(p, 50, 500)
    table.drawOn(p, 50, 550)

    p.showPage()
    p.save()
    
    return response
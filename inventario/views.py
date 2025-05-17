from django.shortcuts import render, redirect, get_object_or_404
from .models import Articulo, Categoria


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
from .models import Articulo
import openpyxl
from django.http import HttpResponse
from .models import Articulo
from django.shortcuts import render, redirect
from django.contrib.auth import login
from .forms import RegistroForm
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .forms import ArticuloForm
from .models import Articulo


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

            # Validación de correos electrónicos
            email = form.cleaned_data.get("email")
            email_confirm = form.cleaned_data.get("email_confirm")
            username = form.cleaned_data.get("username")

            # Verificar si el email ya está registrado
            if User.objects.filter(email=email).exists():
                form.add_error("email", "Este correo electrónico ya está registrado.")

            # Verificar si el username ya está registrado
            if User.objects.filter(username=username).exists():
                form.add_error("username", "Este nombre de usuario ya está en uso.")

            # Verificar que los correos electrónicos coincidan
            if email != email_confirm:
                form.add_error("email_confirm", "Los correos electrónicos no coinciden.")
            
            if not form.errors:  # Guardar usuario solo si no hay errores
                usuario.set_password(form.cleaned_data["password1"])  # Encripta la contraseña
                usuario.save()
                login(request, usuario)  # Autenticación automática tras el registro
                return redirect("redirigiendo")  # Redirige a la página correspondiente

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
    asignacion_filtrada = request.GET.get("asignacion", None)
    categoria_filtrada = request.GET.get("categoria", None)
    
    articulos = Articulo.objects.all()

    # Filtrar por asignación si está presente
    if asignacion_filtrada:
        articulos = articulos.filter(asignacion=asignacion_filtrada)

    # Filtrar por categoría si está presente
    if categoria_filtrada:
        articulos = articulos.filter(categoria__nombre=categoria_filtrada)

    asignaciones_disponibles = Articulo.objects.values_list("asignacion", flat=True).distinct()
    categorias_disponibles = Categoria.objects.values_list("nombre", flat=True).distinct()

    return render(request, "inventario/articulos.html", {
        "articulos": articulos,
        "asignaciones_disponibles": asignaciones_disponibles,
        "categorias_disponibles": categorias_disponibles,
        "asignacion_filtrada": asignacion_filtrada,
        "categoria_filtrada": categoria_filtrada,
    })




@login_required
def cargar_articulo(request):
    if request.method == "POST":
        form = ArticuloForm(request.POST, request.FILES)
        if form.is_valid():
            articulo = form.save(commit=False)  # No guardamos todavía
            articulo.usuario = request.user  # Asignamos el usuario autenticado

            # Validamos la categoría
            categoria = form.cleaned_data.get("categoria")
            if categoria:
                articulo.categoria = categoria  # Asignamos la categoría seleccionada
            
            articulo.save()  # Ahora sí guardamos
            return redirect("articulos")  # Redirige a la lista de artículos

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
    
    contexto = {
        "articulo": articulo,
        "categoria": articulo.categoria.nombre if articulo.categoria else "Sin categoría",
        "usuario_creador": articulo.usuario.username if articulo.usuario else "No asignado",
    }
    
    return render(request, "inventario/detalle_articulo.html", contexto)



@login_required
def editar_articulo(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)

    # Validar que el usuario solo edite artículos que le pertenecen
    if articulo.usuario != request.user:
        return redirect("articulos")  # Redirige si el usuario no tiene permiso

    if request.method == "POST":
        form = ArticuloForm(request.POST, request.FILES, instance=articulo)
        if form.is_valid():
            articulo = form.save(commit=False)

            # Validación de la categoría
            categoria = form.cleaned_data.get("categoria")
            if categoria:
                articulo.categoria = categoria
            
            articulo.save()
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



def generar_xls(request):
    asignacion_filtrada = request.GET.get("asignacion", None)
    articulos = Articulo.objects.all()

    if asignacion_filtrada:
        articulos = articulos.filter(asignacion=asignacion_filtrada)

    if not articulos.exists():
        response = HttpResponse("No hay artículos disponibles para esta asignación.", content_type="text/plain")
        return response

    # Crear archivo Excel
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lista de Artículos"

    # Ajustar ancho de la columna B
    ws.column_dimensions["B"].width = 30  # Ajustar la columna de nombres

    # Encabezados
    headers = ["ID", "Nombre", "Cantidad", "Asignación", "Valor"]
    ws.append(headers)

    # Agregar datos
    for articulo in articulos:
        ws.append([articulo.id, articulo.nombre, articulo.cantidad, articulo.asignacion, articulo.valor])

    # Configurar respuesta HTTP
    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="lista_articulos.xlsx"'
    wb.save(response)

    return response


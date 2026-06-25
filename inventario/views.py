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

import openpyxl
from .forms import EmailRecuperacionForm, CodigoForm, NuevaPasswordForm
from .models import CodigoRecuperacion
import random
from django.utils import timezone




from django.contrib import messages


from django.views.decorators.cache import cache_control

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
    
    return render(request, "inventario/index.html", {"form": form, "show_inicio": False})

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

    return render(request, "inventario/registro.html", {"form": form, "show_inicio": True})

def redirigiendo(request):
    if request.user.is_authenticated and request.user.email:
        try:
            subject = "¡Registro exitoso!"
            message = f"Hola {request.user.username},\n\n¡Tu registro ha sido exitoso! Bienvenido."
            recipient_email = request.user.email
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient_email])
        except Exception as e:
            print(f"ERROR EMAIL: {e}")
        
    return render(request, "inventario/redirigiendo.html")
    


@login_required(login_url='/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def listar_articulos(request):
    asignacion_filtrada = request.GET.get("asignacion", None)
    categoria_filtrada = request.GET.get("categoria", None)
    q = request.GET.get("q", None)
    articulos = Articulo.objects.all().order_by("id")

    if asignacion_filtrada:
        articulos = articulos.filter(asignacion=asignacion_filtrada)

    if categoria_filtrada:
        articulos = articulos.filter(categoria=categoria_filtrada)

    if q:
        articulos = articulos.filter(nombre__icontains=q)

    asignaciones_disponibles = Articulo.objects.order_by("asignacion").values_list("asignacion", flat=True).distinct()
    categorias_disponibles = Articulo.objects.order_by("categoria").values_list("categoria", flat=True).distinct()

    return render(request, "inventario/articulos.html", {
        "articulos": articulos,
        "asignaciones_disponibles": asignaciones_disponibles,
        "categorias_disponibles": categorias_disponibles,
        "asignacion_filtrada": asignacion_filtrada,
        "categoria_filtrada": categoria_filtrada,
        "q": q,
    })
@login_required(login_url='/')
def articulos_card(request):
    asignacion_filtrada = request.GET.get("asignacion", None)
    categoria_filtrada = request.GET.get("categoria", None)
    articulos = Articulo.objects.all().order_by("id")

    if asignacion_filtrada:
        articulos = articulos.filter(asignacion=asignacion_filtrada)

    if categoria_filtrada:
        articulos = articulos.filter(categoria=categoria_filtrada)

    asignaciones_disponibles = Articulo.objects.order_by("asignacion").values_list("asignacion", flat=True).distinct()
    categorias_disponibles = Articulo.objects.order_by("categoria").values_list("categoria", flat=True).distinct()

    return render(request, "inventario/articulos.html", {
        "articulos": articulos,
        "asignaciones_disponibles": asignaciones_disponibles,
        "categorias_disponibles": categorias_disponibles,
        "asignacion_filtrada": asignacion_filtrada,
        "categoria_filtrada": categoria_filtrada,
    })



@login_required(login_url='/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def cargar_articulo(request):
    if request.method == "POST":
        form = ArticuloForm(request.POST, request.FILES)
        if form.is_valid():
            articulo = form.save(commit=False)
            articulo.usuario = request.user  
            articulo.save()

            messages.success(request, "✅ Artículo cargado correctamente.")
            return redirect("confirmacion_articulo")  # Redirige a la página de confirmación
        else:
            messages.error(request, "❌ Hubo un error al cargar el artículo.")

    else:
        form = ArticuloForm()

    return render(request, "inventario/cargar_articulo.html", {"form": form})

@login_required(login_url='/')
def logout_view(request):
    logout(request)
    return redirect("index")

@login_required(login_url='/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def detalle_articulo(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)
    return render(request, "inventario/detalle_articulo.html", {"articulo": articulo})

@login_required(login_url='/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
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

@login_required(login_url='/')
@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def eliminar_articulo(request, articulo_id):
    articulo = get_object_or_404(Articulo, id=articulo_id)
    if request.method == "POST":
        articulo.delete()
        return redirect("articulos")

    return render(request, "inventario/eliminar_articulo.html", {"articulo": articulo})


@login_required(login_url='/')
def generar_xls(request):
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    asignacion_filtrada = request.GET.get("asignacion", None)
    articulos = Articulo.objects.all()

    if asignacion_filtrada:
        articulos = articulos.filter(asignacion=asignacion_filtrada)

    if not articulos.exists():
        return HttpResponse("No hay artículos disponibles.", content_type="text/plain")

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Lista de Artículos"

    # Estilos
    header_font = Font(bold=True, color="FFFFFF", size=12)
    header_fill = PatternFill("solid", fgColor="2563EB")
    header_align = Alignment(horizontal="center", vertical="center")

    alt_fill = PatternFill("solid", fgColor="EFF6FF")
    center_align = Alignment(horizontal="center", vertical="center")

    border_side = Side(style="thin", color="BFDBFE")
    cell_border = Border(
        left=border_side, right=border_side,
        top=border_side, bottom=border_side
    )

    # Encabezados
    headers = ["ID", "Nombre", "Cantidad", "Asignación", "Valor"]
    ws.append(headers)

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.font = header_font
        cell.fill = header_fill
        cell.alignment = header_align
        cell.border = cell_border

    ws.row_dimensions[1].height = 28

    # Datos
    for row_num, articulo in enumerate(articulos, 2):
        ws.append([
            articulo.id,
            articulo.nombre,
            articulo.cantidad,
            articulo.asignacion,
            float(articulo.valor)
        ])

        fill = alt_fill if row_num % 2 == 0 else PatternFill("solid", fgColor="FFFFFF")

        for col_num in range(1, 6):
            cell = ws.cell(row=row_num, column=col_num)
            cell.fill = fill
            cell.border = cell_border
            cell.alignment = center_align
            if col_num == 5:
                cell.number_format = '"$"#,##0.00'

        ws.row_dimensions[row_num].height = 22

    # Ancho de columnas
    col_widths = [8, 30, 12, 18, 14]
    for i, width in enumerate(col_widths, 1):
        ws.column_dimensions[get_column_letter(i)].width = width

    # Congelar fila de encabezado
    ws.freeze_panes = "A2"

    response = HttpResponse(content_type="application/vnd.ms-excel")
    response["Content-Disposition"] = 'attachment; filename="lista_articulos.xlsx"'
    wb.save(response)

    return response

def confirmacion_articulo(request):
    return render(request, "inventario/confirmacion_articulo.html")


def solicitar_recuperacion(request):
    if request.method == "POST":
        form = EmailRecuperacionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            try:
                usuario = User.objects.get(email=email)
            except User.DoesNotExist:
                form.add_error("email", "No existe una cuenta con ese email.")
                return render(request, "inventario/solicitar_recuperacion.html", {"form": form})

            codigo = str(random.randint(100000, 999999))
            CodigoRecuperacion.objects.create(usuario=usuario, codigo=codigo)

            html_message = f"""
<!DOCTYPE html>
<html>
<body style="margin:0;padding:0;background:#f1f5f9;font-family:Arial,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 0">
    <tr>
      <td align="center">
        <table width="480" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;border:1px solid #e2e8f0">
          
          <tr>
            <td style="background:#2563EB;padding:28px 32px;text-align:center">
              <h1 style="color:#ffffff;font-size:22px;margin:0;font-weight:700">Recuperación de contraseña</h1>
            </td>
          </tr>

          <tr>
            <td style="padding:32px">
              <p style="color:#374151;font-size:15px;margin:0 0 16px">Hola <strong>{usuario.username}</strong>, recibimos una solicitud para restablecer tu contraseña.</p>
              <p style="color:#374151;font-size:15px;margin:0 0 24px">Tu código de verificación es:</p>

              <div style="background:#EFF6FF;border:2px dashed #2563EB;border-radius:10px;padding:24px;text-align:center;margin-bottom:24px">
                <span style="font-size:36px;font-weight:700;letter-spacing:10px;color:#1D4ED8">{codigo}</span>
              </div>

              <div style="background:#FEF3C7;border-left:4px solid #F59E0B;border-radius:4px;padding:12px 16px;margin-bottom:24px">
                <p style="color:#92400E;font-size:13px;margin:0">Este código vence en <strong>10 minutos</strong>. No lo compartas con nadie.</p>
              </div>

              <p style="color:#6B7280;font-size:13px;margin:0">Si no solicitaste este código, podés ignorar este email. Tu cuenta está segura.</p>
            </td>
          </tr>

          <tr>
            <td style="background:#F8FAFC;padding:16px 32px;text-align:center;border-top:1px solid #E2E8F0">
              <p style="color:#9CA3AF;font-size:12px;margin:0">© 2025 Inventario · Todos los derechos reservados</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""

            send_mail(
                subject="Código de recuperación de contraseña",
                message=f"Hola {usuario.username}, tu código es: {codigo}\n\nVence en 10 minutos.",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_message,
            )

            request.session["recuperacion_user_id"] = usuario.id
            return redirect("verificar_codigo")
    else:
        form = EmailRecuperacionForm()

    return render(request, "inventario/solicitar_recuperacion.html", {"form": form})


def verificar_codigo(request):
    user_id = request.session.get("recuperacion_user_id")
    if not user_id:
        return redirect("solicitar_recuperacion")

    if request.method == "POST":
        form = CodigoForm(request.POST)
        if form.is_valid():
            codigo_ingresado = form.cleaned_data["codigo"]
            try:
                registro = CodigoRecuperacion.objects.filter(
                    usuario_id=user_id,
                    codigo=codigo_ingresado,
                    usado=False
                ).latest("creado_en")

                if registro.esta_vigente():
                    registro.usado = True
                    registro.save()
                    request.session["recuperacion_verificado"] = True
                    return redirect("nueva_password")
                else:
                    form.add_error("codigo", "El código expiró. Solicitá uno nuevo.")
            except CodigoRecuperacion.DoesNotExist:
                form.add_error("codigo", "Código incorrecto.")
    else:
        form = CodigoForm()

    return render(request, "inventario/verificar_codigo.html", {"form": form})


def nueva_password(request):
    user_id = request.session.get("recuperacion_user_id")
    verificado = request.session.get("recuperacion_verificado")

    if not user_id or not verificado:
        return redirect("solicitar_recuperacion")

    if request.method == "POST":
        form = NuevaPasswordForm(request.POST)
        if form.is_valid():
            usuario = get_object_or_404(User, id=user_id)
            usuario.set_password(form.cleaned_data["password"])
            usuario.save()
            del request.session["recuperacion_user_id"]
            del request.session["recuperacion_verificado"]
            return redirect("index")
    else:
        form = NuevaPasswordForm()

    return render(request, "inventario/nueva_password.html", {"form": form})
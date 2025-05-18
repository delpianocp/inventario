from django.urls import path
from .views import index, registro,confirmacion_articulo, listar_articulos, cargar_articulo, logout_view, detalle_articulo, editar_articulo, eliminar_articulo, generar_xls, redirigiendo, articulos_card


urlpatterns = [
    path("", index, name="index"),
    path("registro", registro, name="registro"),
    path("articulos", listar_articulos, name="articulos"),
    path("cargar_articulo", cargar_articulo, name="cargar_articulo"),
    path("logout/", logout_view, name="logout"),
    path("articulo/<int:articulo_id>/", detalle_articulo, name="detalle_articulo"),
    path("articulo/<int:articulo_id>/editar/", editar_articulo, name="editar_articulo"),
    path("articulo/<int:articulo_id>/eliminar/", eliminar_articulo, name="eliminar_articulo"),
    path("generar_xls/", generar_xls, name="generar_xls"),
    path("redirigiendo/", redirigiendo, name="redirigiendo"),
    path("articulos_card", articulos_card, name="articulos_card"),
    path("confirmacion_articulo", confirmacion_articulo, name="confirmacion_articulo"),





]

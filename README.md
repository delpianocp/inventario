# 📦 Inventario

> Sistema de inventario sencillo desarrollado con **Django 5** · Generación de reportes en PDF · Deploy con Gunicorn

---

## 📌 Descripción

Aplicación web para gestionar un inventario de artículos. Permite registrar, visualizar y administrar productos con soporte para imágenes y generación de reportes en PDF.

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| **Django 5.2** | Framework web backend |
| **Gunicorn** | Servidor WSGI para producción |
| **Pillow** | Manejo de imágenes de artículos |
| **ReportLab** | Generación de reportes en PDF |
| **psycopg2** | Conector para PostgreSQL |
| **SQLite** | Base de datos para desarrollo |

---

## 📁 Estructura del proyecto

```
inventario/
│
├── app/                   # Configuración principal de Django (settings, urls, wsgi)
├── inventario/            # Aplicación principal (modelos, vistas, urls)
├── media/
│   └── articulos/         # Imágenes de los artículos subidas por el usuario
│
├── manage.py              # Utilidad de línea de comandos de Django
├── Procfile               # Comando de inicio para deploy (Gunicorn)
├── requirements.txt       # Dependencias del proyecto
└── db.sqlite3             # Base de datos SQLite (desarrollo)
```

---

## 🚀 Instalación local

### 1. Clonar el repositorio

```bash
git clone https://github.com/delpianocp/inventario.git
cd inventario
```

### 2. Crear entorno virtual e instalar dependencias

```bash
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

pip install -r requirements.txt
```

### 3. Aplicar migraciones

```bash
python manage.py migrate
```

### 4. Crear superusuario (administrador)

```bash
python manage.py createsuperuser
```

### 5. Iniciar el servidor

```bash
python manage.py runserver
```

Abrir en el navegador: `http://localhost:8000`

---

## 🌐 Deploy en producción

El proyecto incluye un `Procfile` listo para plataformas como **Railway** o **Heroku**:

```
web: gunicorn app.wsgi
```

Para producción se recomienda usar **PostgreSQL** en lugar de SQLite. Configurar las variables de entorno:

```env
SECRET_KEY=tu_clave_secreta
DEBUG=False
DATABASE_URL=postgresql://usuario:password@host:5432/nombre_db
ALLOWED_HOSTS=tu-dominio.com
```

---

## 📄 Dependencias

```
Django==5.2.1
gunicorn==23.0.0
Pillow==11.2.1
reportlab==4.4.0
psycopg2==2.9.10
```

---

## 👤 Autor

**delpianocp** — [github.com/delpianocp](https://github.com/delpianocp)

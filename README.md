# Datamundi / CityLens

Aplicación web para explorar ciudades del mundo. Muestra información relevante de la ciudad buscada y un mapa con los mejores sitios turísticos por categoría: familiar, gastronómico, nocturno y alternativo.

---

## Stack tecnológico

| Capa | Tecnología |
|---|---|
| Backend | Python + Flask |
| Templates | Jinja2 (incluido en Flask) |
| Base de datos | PostgreSQL + Flask-SQLAlchemy |
| Frontend | HTML + CSS + Bootstrap 5 + Tailwind CDN |
| APIs externas | Google Places API, REST Countries |

---

## Estructura del proyecto

```
citylens/
├── app/
│   ├── __init__.py          ← App factory, registra blueprints y extensiones
│   ├── models.py            ← Modelos SQLAlchemy (City, Place)
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── main.py          ← Rutas que renderizan templates (/, /city)
│   │   ├── cities.py        ← API: GET /api/city
│   │   └── places.py        ← API: GET /api/places
│   ├── services/
│   │   ├── __init__.py
│   │   ├── city_service.py      ← Lógica de búsqueda y caché de ciudades
│   │   ├── places_service.py    ← Lógica de búsqueda y caché de lugares
│   │   └── google_places.py     ← Wrapper para Google Places API
│   ├── templates/
│   │   ├── base.html        ← Template base (Bootstrap, fuentes, CSS global)
│   │   ├── index.html       ← Página de búsqueda
│   │   └── city.html        ← Página de detalle con mapa
│   └── static/
│       ├── css/
│       │   └── global.css
│       └── js/
│           ├── inicio.js
│           └── city.js
├── .env                     ← Variables de entorno (NO subir al repo)
├── .env.example             ← Plantilla de variables de entorno
├── .gitignore
├── config.py                ← Configuración de Flask desde .env
├── requirements.txt
└── run.py                   ← Punto de entrada
```

---

## Requisitos

- Python 3.10+
- PostgreSQL corriendo localmente
- Una base de datos creada (por ejemplo `citylens`)

---

## Configuración inicial

### 1. Clonar el repositorio

```bash
git clone <url-del-repo>
cd citylens
```

### 2. Crear el entorno virtual

```bash
python -m venv venv
```

Activar:

```bash
# Linux / Mac
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

```bash
cp .env.example .env
```

Editar `.env` con tus datos:

```
FLASK_ENV=development
SECRET_KEY=cambia_esto
DATABASE_URL=postgresql://usuario:password@localhost:5432/citylens
GOOGLE_PLACES_KEY=tu_api_key
```

---

## Ejecutar el proyecto

```bash
python run.py
```

Abrir en el navegador:

```
http://localhost:5000
```

Flask sirve tanto el frontend (HTML) como la API desde el mismo servidor. No se necesita un segundo puerto.

---

## Endpoints disponibles

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Página de búsqueda |
| GET | `/city?name=Tokyo` | Página de detalle de ciudad |
| GET | `/api/city?name=Tokyo` | Datos JSON de la ciudad |
| GET | `/api/places?city=Tokyo&category=familiar` | JSON con hasta 10 lugares |

Las categorías válidas para `/api/places` son: `familiar`, `gastronomico`, `nocturna`, `alternativo`.

---

## Flujo de trabajo con Git

Este proyecto usa un flujo basado en ramas:

- `main` — rama estable. Nunca se trabaja directamente aquí.
- `dev` — rama de desarrollo. Todo el trabajo se integra aquí primero.
- `feature/nombre-tarea` — ramas individuales por tarea, derivadas de `dev`.

### Flujo por tarea

```bash
# 1. Asegurarse de estar en dev actualizado
git checkout dev
git pull origin dev

# 2. Crear rama para la tarea
git checkout -b feature/nombre-de-la-tarea

# 3. Trabajar, hacer commits
git add .
git commit -m "feat: descripción del cambio"

# 4. Subir la rama
git push origin feature/nombre-de-la-tarea

# 5. Crear Pull Request hacia dev en GitHub
# 6. El PM revisa y hace merge
```

Nadie hace merge a `main` directamente. `main` solo se actualiza desde `dev` cuando hay una versión estable.

---

## Verificación de base de datos

Una vez que el DBA configure los modelos, se podrá verificar la conexión con:

```bash
python -m app.db_check
```

Este script se creará como parte de la issue `[DB] Crear script de verificación de base de datos`.

---

## Problemas comunes

### `ModuleNotFoundError`
Asegúrate de tener el entorno virtual activado antes de correr cualquier comando.

### Error de conexión a PostgreSQL
Verifica que el servicio de PostgreSQL esté corriendo y que las credenciales en `.env` sean correctas. El usuario debe tener permisos sobre la base de datos especificada.

### La página carga pero los datos no aparecen
Los endpoints `/api/city` y `/api/places` están en construcción. El frontend muestra datos de prueba (mocks) mientras tanto — esto es comportamiento esperado.

---

## Estado actual

| Componente | Estado |
|---|---|
| Estructura base del proyecto | ✅ Listo |
| Templates Jinja2 (index, city) | ✅ Listo |
| Estilos y JS del frontend | ✅ Listo |
| Modelos de base de datos | 🔧 En progreso |
| Endpoint `/api/city` | 🔧 En progreso |
| Endpoint `/api/places` | 🔧 En progreso |
| Integración Google Places API | 🔧 En progreso |
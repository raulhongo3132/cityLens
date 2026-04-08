# CityLens – Setup inicial
## Provicional

Este proyecto es el esqueleto base de **CityLens**, con:

* Backend en Flask (puerto 5000)
* Frontend estático (puerto 5500)
* CORS configurado
* Preparado para PostgreSQL

---

## Flujo de trabajo con Git

Este proyecto utiliza un flujo basado en ramas:

* `dev`: rama de desarrollo donde se implementan cambios
* `main`: rama estable lista para producción

Ningún cambio debe hacerse directamente sobre `main`. Todo desarrollo ocurre en `dev` (o ramas derivadas), y posteriormente se integra mediante un Pull Request (PR).

Ojo: las ramas derivdas pueden ser: 

`feature/nombre-de-la-tarea  →  dev  →  main`

Para subir cambios:

1. Trabajar en la rama `dev`
2. Hacer commit y push:

   ```bash
   git push origin dev
   ```
3. En GitHub, crear un **Pull Request** desde `dev` hacia `main`
4. Revisar los cambios (idealmente por otro desarrollador)
5. Hacer merge del PR

Este flujo asegura control de calidad, revisión de código y estabilidad en la rama principal.


# Estructura del proyecto

```
mi_proyecto/
├── .env
├── .env.example
├── backend/
│   ├── venv/
│   ├── __init__.py
│   ├── run.py
│   ├── config.py
│   └── app/
│       └── __init__.py
└── frontend/
    └── css/
    └── js/
    └── pages/
    └── index.html
```

---

# 1. Requisitos

* Python 3.10+
* PostgreSQL
* Code - OSS (opcional, puede ser VSC)

---

# 2. Descargar el repositorio

Debes tener configurado tu git con tu github (comando por autenticación con SSH). Para clonar el repositorio, ejecuta el siguiente comando

```bash
    git clone git@github.com:raulhongo3132/cityLens.git
    cd citiLens
```


---

# 3. Bade de datos y variables de entorno

Debes tener una instancia de PostgreSQL corriendo localmente.

Crea una base de datos (por ejemplo `citylens`) y un usuario con permisos.

Luego usa esos datos en tu archivo `.env`.

1. Copia el archivo de ejemplo:

```bash
cp .env.example .env
```

2. Edita `.env` con tus credenciales:

```
FLASK_ENV=development
DATABASE_URL=postgresql://usuario:password@localhost:5432/tu_basedatos
SECRET_KEY=tu_clave_secreta
```

---

# 4. Entorno virtual

El entorno virtual vive dentro de `backend/`.

### Crear (si no existe):

```bash
cd backend
python -m venv venv
```

### Activar:

**Linux / Mac:**

```bash
source venv/bin/activate
```

**Windows:**

```bash
venv\Scripts\activate
```

---

# 5. Instalar dependencias

Con el entorno virtual activado:

```bash
pip install -r requirements.txt
```

---

# 6. Ejecutar el proyecto

## Backend

Desde la raíz del proyecto:

```bash
python -m backend.run
```

Corre en:

```
http://localhost:5000
```

---

## Frontend

### Opción A (recomendada)

Usar Live Server en VS Code:

* Abrir `frontend/index.html`
* Click derecho → **Open with Live Server**

```
http://localhost:5500
```

---

### Opción B

```bash
cd frontend
python -m http.server 5500
```

---

# 7. Prueba de conexión

Abre en el navegador:

```
http://localhost:5500
```

Esto hará una petición a:

```
http://localhost:5000/api/ping
```

---

# Resultado esperado

En pantalla:

```
{"status": "ok"}
```

En consola del navegador:

```
Respuesta del backend: {status: "ok"}
```

---

# Problemas comunes

## Error de CORS

Si aparece un error como:

```
blocked by CORS policy
```

Verifica que el backend permita ambos orígenes:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "http://localhost:5500",
            "http://127.0.0.1:5500"
        ]
    }
})
```

Y reinicia el servidor.

---

## localhost vs 127.0.0.1

Para CORS, estos son distintos:

* http://localhost:5500
* http://127.0.0.1:5500

---

# Notas de desarrollo

* Ejecutar siempre desde la raíz:

  ```bash
  python -m backend.run
  ```

* `backend/__init__.py` existe para definir el paquete Python

* No ejecutar `run.py` directamente dentro de `backend/`

---

# Estado actual

✔ Backend funcionando
✔ Endpoint `/api/ping`
✔ CORS configurado
✔ Frontend conectado

---


# Películas: Flask + MongoDB + SPARQL

Aplicación web de valoración de películas hecha con **Flask** y **MongoDB** (a través del ODM **MongoEngine**), que enriquece cada película con datos externos de **Wikidata** consultados por **SPARQL**. Proyecto de la asignatura de Bases de Datos No Relacionales (BDNR), Grado en Ingeniería de Sistemas de Datos, ETSIT-UPM.

La app sigue el patrón **MVC**: modelos (MongoEngine), vistas (plantillas HTML con Bootstrap) y controladores (lógica y consultas).

## Qué hace

- **Películas:** listado, filtrado por título, género o director, y ficha de detalle.
- **Datos externos:** en la ficha se consulta Wikidata con SPARQL para mostrar país, presupuesto, recaudación, identificador de IMDb y distribuidora.
- **Usuarios:** registro, inicio y cierre de sesión (contraseñas con hash de Werkzeug), consulta y edición del perfil.
- **Reseñas:** comentarios con puntuación del 1 al 10, guardados como documentos embebidos dentro de cada película.
- **Favoritos:** añadir y quitar películas de la lista de favoritas de un usuario.
- **Generador de datos:** `generar_seeder.py` lanza una consulta SPARQL a Wikidata y genera películas nuevas (JSON para MongoDB y un fichero RDF en formato Turtle).

## Modelo de datos

Tres colecciones de documentos con diseño orientado a lectura:

- `Movie`: datos de la película, actores y reseñas **embebidos**, para pintar la ficha sin hacer joins.
- `User`: datos del usuario y su lista de películas favoritas.
- `Review` (embebida en `Movie`): referencia al usuario y copia de su `username`, para no tener que consultar la colección de usuarios al mostrar cada reseña.

## Estructura

```
flaskr/
├── run.py                  Arranque de la app y registro de rutas
├── db.py                   Configuración de Flask y de la conexión a MongoDB
├── models.py               Modelos MongoEngine (User, Movie, Actor, Review)
├── controllers/            Lógica de negocio: CRUD y consultas
├── routes/                 Endpoints (películas, usuarios, login)
├── sparql.py               Cliente de consultas SPARQL a Wikidata
├── generar_seeder.py       Generador de películas desde Wikidata
├── seeders/                Datos iniciales (JSON) y notas de importación
├── templates/ y static/    Vistas, estilos y recursos
└── requirements.txt
movies.ttl                  Datos de películas en RDF (generados desde Wikidata)
```

## Tecnologías

Python 3 · Flask · MongoEngine / Flask-MongoEngine · MongoDB · SPARQL (Wikidata) · rdflib · SPARQLWrapper · Bootstrap

## Cómo ejecutarlo

Necesitas Python 3.10 o superior, MongoDB Community en local y conexión a internet (para las consultas a Wikidata). Todos los comandos se lanzan desde la raíz del repositorio.

```bash
# 1. Entorno virtual y dependencias
python -m venv venv
source venv/bin/activate          # En Windows: .\venv\Scripts\activate
pip install -r flaskr/requirements.txt

# 2. Con MongoDB arrancado, importar los datos iniciales
mongoimport -d moviesbdnr -c user  --file ./flaskr/seeders/user.json  --jsonArray
mongoimport -d moviesbdnr -c movie --file ./flaskr/seeders/movie.json --jsonArray
# Opcional: películas generadas desde Wikidata
mongoimport -d moviesbdnr -c movie --file ./flaskr/seeders/extra_movies.json --jsonArray

# 3. Arrancar la app
flask --app ./flaskr/run.py run --debug
```

Abre `http://localhost:5000`. Los usuarios de ejemplo son ficticios; para entrar puedes crear el tuyo desde la página de registro.

Si necesitas otro puerto: `flask --app ./flaskr/run.py run --debug --port=5002`.

Para restablecer los datos, borra la base de datos `moviesbdnr` y repite el paso 2.

### Generar más películas

```bash
python flaskr/generar_seeder.py
```

Escribe `flaskr/seeders/extra_movies.json` y `movies.ttl` con 5 películas de acción posteriores a 2015 consultadas en Wikidata.

### Configuración

La clave secreta de Flask se lee de la variable de entorno `SECRET_KEY`. Si no existe, usa un valor de desarrollo, que no debe usarse en producción:

```bash
export SECRET_KEY="una-clave-larga-y-aleatoria"
```

## Posibles mejoras

- Tests propios con `pytest` y una base de datos de pruebas.
- Leer también la configuración de MongoDB desde variables de entorno.
- Desactivar el modo `DEBUG` fuera del desarrollo local.
- Cachear las respuestas de Wikidata para acelerar la ficha de película.
- Añadir paginación al listado de películas.

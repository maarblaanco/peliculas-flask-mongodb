from models import User
import datetime
from bson import ObjectId
import uuid
from flask import request

# Al empezar debes descomentar el código, se sigueire ir descomentando función por función para que no de error

def read_users(name=None):
    print("Obteniendo todos los users...")
    print("Filtro por nombre:", name)

    #Completar la función, si name es None busca todos, si tiene algun valor filtra por el campo "name"
    if name:
    	users = User.objects(name=name)
    else:
    	users = User.objects.all()
    	
    return users


def read_user(username):
    print("Obteniendo el user...", username)
    user = User.objects(username=username).first()
    return user

def create_user(username, name, surname, email, password_hash):
    print("Creando usuario...", username)
    #Completar la función
    
    user = User(
    	_id=ObjectId(),
        username=username,
        name=name,
        surname=surname,
        email=email,
        password_hash=password_hash,
        created_at=datetime.datetime.now(),
        updated_at=datetime.datetime.now()
    )
    user.save()

    return user

def update_user(username, name, surname, email, password_hash, country, city):
    print("Actualizando usuario...", username)
    #Completar la función
    
    user = User.objects(username=username).first()
    if not user:
        return None
    
    user.name = name
    user.surname = surname
    user.email = email
    user.password_hash = password_hash
    user.country = country
    user.city = city
    user.updated_at = datetime.datetime.now()
    user.save()

    return user

def add_favorite_movie_to_user(username, movie_id, movie_title, movie_slug):
    print("Añadiendo película favorita al usuario...", username)
    
    user = User.objects(username=username).first()
    if not user:
        print("Usuario no encontrado")
        return None

    # Comprobar si ya existe la película en favoritos (por _id o movie_id)
    for fav in user.favorite_movies:
        if str(fav.get("movie_id")) == str(movie_id) or str(fav.get("_id")) == str(movie_id):
            print("Película ya está en favoritos")
            return user

    # Crear el objeto de favorito (incluyendo _id)
    favorite = {
        "_id": ObjectId(movie_id),
        "movie_id": str(movie_id),
        "title": movie_title,
        "slug": movie_slug
    }

    user.favorite_movies.append(favorite)
    user.updated_at = datetime.datetime.now()
    user.save()

    return user


def remove_favorite_movie_from_user(username, movie_id):
    print("Quitando película favorita al usuario...", username)
    
    user = User.objects(username=username).first()
    if not user:
        print("Usuario no encontrado")
        return None

    # Filtrar las películas, eliminando la que coincida por _id o movie_id
    user.favorite_movies = [
        fav for fav in user.favorite_movies
        if str(fav.get("_id")) != str(movie_id) and str(fav.get("movie_id")) != str(movie_id)
    ]

    user.updated_at = datetime.datetime.now()
    user.save()

    return user
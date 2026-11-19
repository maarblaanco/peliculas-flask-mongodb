from models import Movie, User
from models import Review
from sparql import query
from flask import g, request
import datetime
from bson import ObjectId


def read_movies():
    print("Reading movies...")
    movies = Movie.objects()
    return movies

def read_movies_by_filter(title, genre, director):
    #Completar la función
    params = [title, genre, director]
    non_none_params = sum(1 for p in params if p is not None)
    
    if non_none_params > 1:
        raise ValueError("Solo se permite un filtro a la vez")
        
    if title is not None:
        movies = Movie.objects(title__icontains=title)
    elif genre is not None:
        if genre.lower() == "all":
            movies = Movie.objects()  # Devuelve todas las películas
        else:
            movies = Movie.objects(genres__icontains=genre)

    elif director is not None:
        movies = Movie.objects(director__icontains=director)
    else:
        movies = Movie.objects()  # Devuelve todas las películas
    
    return list(movies)


def read_movie(slug):
    print("Reading movie...", slug)
    
    movie = Movie.objects(slug=slug).first()
    if not movie:
        return None
        
    uri = movie.uri
    
    # CONSULTA SPARQL 
    sparql_query = f'''
SELECT 
  ?pais ?presupuesto ?recaudacion ?imdbId ?distribuidor 
WHERE {{
  OPTIONAL {{
    <{uri}> wdt:P495 ?country .
    ?country rdfs:label ?pais .
    FILTER(LANG(?pais) = "es")
  }}
  OPTIONAL {{ <{uri}> wdt:P2130 ?presupuesto . }}
  OPTIONAL {{ <{uri}> wdt:P2142 ?recaudacion . }}
  OPTIONAL {{ <{uri}> wdt:P345 ?imdbId . }}
  OPTIONAL {{
    <{uri}> wdt:P750 ?distributor .
    ?distributor rdfs:label ?distribuidor .
    FILTER(LANG(?distribuidor) = "es")
  }}
}}
LIMIT 1
'''
    
    print(f"Query: {sparql_query}")
    
    try:
        results = query(sparql_query)
        movie.extra = results
    except Exception as e:
        print(f"ERROR: {e}")
        movie.extra = []
    
    # Comprobar si la película es favorita del usuario actual
    movie.is_favorite = False
    if hasattr(g, "user") and g.user:
        username = g.user["username"]
        user = User.objects(username=username).first()
        if user:
            movie.is_favorite = False

            for fav in user.favorite_movies:
                fav_id = fav.get("_id") or fav.get("movie_id")

                if ObjectId(fav_id) == movie.id:
                    movie.is_favorite = True
                    break
    
    return movie
    
    

def create_review(movie_slug, user_id, username, comment, rating):
    print("Creating review...", movie_slug)
    
    # Validar que ningún parámetro sea None
    if None in (movie_slug, user_id, username, comment, rating):
        return None
    
    # Obtener película por slug
    movie = Movie.objects(slug=movie_slug).first()
    if not movie:
        return None
    
    # Crear y añadir la review
    new_review = Review(
        user_id=user_id,
        username=username,
        comment=comment,
        rating=rating
    )
    movie.reviews.append(new_review)
    
    movie.updated_at = datetime.datetime.now()
    movie.save()
    
    return movie



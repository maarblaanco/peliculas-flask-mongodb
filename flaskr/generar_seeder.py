import json
from datetime import datetime
from SPARQLWrapper import SPARQLWrapper, JSON

def get_actors(qid):
    """Devuelve lista de actores principales de la película desde Wikidata"""
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)
    
    query_str = f"""
    SELECT ?actor ?actorLabel ?dob WHERE {{
      wd:{qid} wdt:P161 ?actor .
      OPTIONAL {{ ?actor wdt:P569 ?dob . }}
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "es,en". }}
    }}
    LIMIT 5
    """
    sparql.setQuery(query_str)
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(f"Error consultando actores de {qid}: {e}")
        return []

    actors = []
    for r in results["results"]["bindings"]:
        name = r["actorLabel"]["value"]
        dob = r.get("dob", {}).get("value", "")
        actors.append({
            "name": name,
            "date_of_birth": dob,
            "biography": ""  
        })
    return actors


def generar_datos():
    sparql = SPARQLWrapper("https://query.wikidata.org/sparql")
    sparql.setReturnFormat(JSON)

    # Consulta SPARQL: 5 películas de ejemplo
    query_str = """
    SELECT DISTINCT ?item ?itemLabel ?date ?duration ?image ?directorLabel
    WHERE {
      ?item wdt:P31 wd:Q11424;          # Instancia de película
            wdt:P136 wd:Q188473;       # Género acción (ejemplo)
            wdt:P577 ?date;             # Fecha de estreno
            wdt:P2047 ?duration;        # Duración
            wdt:P18 ?image;             # Imagen
            wdt:P57 ?director.          # Director
      FILTER(?date > "2015-01-01"^^xsd:dateTime)
      SERVICE wikibase:label { bd:serviceParam wikibase:language "es,en". }
    }
    LIMIT 5
    """
    
    print("Consultando a Wikidata (esto puede tardar unos segundos)...")
    sparql.setQuery(query_str)
    
    try:
        results = sparql.query().convert()
    except Exception as e:
        print(f"Error conectando a Wikidata: {e}")
        return

    movies_json_list = []
    ttl_content = ""

    print(f"Se han encontrado {len(results['results']['bindings'])} películas.")

    for result in results["results"]["bindings"]:
        uri = result["item"]["value"]
        title = result["itemLabel"]["value"]
        slug = title.lower().replace(" ", "-").replace(":", "").replace("'", "")
        raw_date = result["date"]["value"]
        release_date = raw_date.split("T")[0]
        
        try:
            duration = int(float(result["duration"]["value"]))
        except:
            duration = 120  # Valor por defecto si falla

        director = result["directorLabel"]["value"]
        image = result["image"]["value"]

        # Obtener actores para esta película
        qid = uri.split("/")[-1]
        actors = get_actors(qid)

        # JSON para MongoDB
        movie_json = {
            "title": title,
            "slug": slug,
            "uri": uri,
            "release_date": {"$date": f"{release_date}T00:00:00Z"},
            "duration": duration,
            "thumbnail": image,
            "director": director,
            "genres": ["Action"],  # simplificado
            "actors": actors,
            "reviews": [],         # vacío al principio
            "created_at": {"$date": datetime.now().isoformat() + "Z"},
            "updated_at": {"$date": datetime.now().isoformat() + "Z"}
        }
        movies_json_list.append(movie_json)
        
        # Generar TTL
        ttl_content += f'<{uri}> <http://schema.org/name> "{title}" .\n'
        ttl_content += f'<{uri}> <http://schema.org/director> "{director}" .\n'
        ttl_content += f'<{uri}> <http://schema.org/datePublished> "{release_date}" .\n'
        ttl_content += f'<{uri}> <http://schema.org/duration> "{duration}" .\n\n'

    # Guardar JSON
    path_json = 'flaskr/seeders/extra_movies.json'
    with open(path_json, 'w', encoding='utf-8') as f:
        json.dump(movies_json_list, f, indent=4, ensure_ascii=False)
    print(f"Generado: {path_json}")
    
    # Guardar TTL
    path_ttl = 'movies.ttl'
    with open(path_ttl, 'w', encoding='utf-8') as f:
        f.write(ttl_content)
    print(f"Generado: {path_ttl}")

if __name__ == "__main__":
    generar_datos()

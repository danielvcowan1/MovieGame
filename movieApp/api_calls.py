from flask import Flask, request, json
import http.client


def get_id(movie, key):
    str = movie
    str = str.replace(" ", "%20")
    str = str.replace(":", "%3A")
    str = str.replace("'", "%27")
    str = str.replace("'", "%2B")
    movie_query = "query="+str
    key="api_key="+key
    api_request = "https://api.themoviedb.org/3/search/movie?api_key=&language=en-US&query&page=1&include_adult=false"
    api_request = api_request.replace("query", movie_query)
    api_request = api_request.replace("api_key=", key)
    return api_request

def get_poster(id_num, key):
    id_num = str(id_num)
    api_request = "https://api.themoviedb.org/3/movie/movie_id?api_key=&language=en-US"
    api_request = api_request.replace("movie_id", id_num)
    api_request = api_request.replace("api_key=", key)
    return api_request

def get_cast(id_num, key):
    id_num = str(id_num)
    api_request = "https://api.themoviedb.org/3/movie/movie_id/credits?api_key=8b644cf36c1cdfe878910278f2fe06cb"
    api_request = api_request.replace("movie_id", id_num)
    return api_request

def get_popular(key):
    api_request = "https://api.themoviedb.org/3/person/popular?api_key=8b644cf36c1cdfe878910278f2fe06cb&language=en-US&page=1"
    return api_request

def get_actor(id): 
    id_num = str(id)
    api_request = "https://api.themoviedb.org/3/person/person_id/movie_credits?api_key=8b644cf36c1cdfe878910278f2fe06cb&language=en-US"
    api_request= api_request.replace("person_id", id_num)
    return api_request

def search_actor(actor):
    actor= "query="+actor
    actor = actor.replace(" ", "%20")
    actor = actor.replace(":", "%3A")
    actor = actor.replace("'", "%27")
    api_request = "https://api.themoviedb.org/3/search/person?api_key=8b644cf36c1cdfe878910278f2fe06cb&language=en-US&query=&page=1&include_adult=false"
    api_request = api_request.replace("query=", actor)
    return api_request

def get_json(call_string):
    conn = http.client.HTTPSConnection("api.themoviedb.org")
    payload = "{}"
    conn.request("GET", call_string, payload)
    res = conn.getresponse()
    file_data = res.read()
    data = json.loads(file_data)
    return data



def get_info(search_query, key, actor):
    
    movie_id = search_query
    cast_call_string = get_cast(movie_id, key)
    cast_data = get_json(cast_call_string)

    cast_members = []
    for i in range(len(cast_data['cast'])):
        cast_members.append(cast_data['cast'][i])

    x=0 
    
    while True: 
        if actor != cast_members[x]['name']:
            break

        x+=1

    return cast_members[x]

def searchresults_get_info(search_query, key):
    
    result = request.args.getlist(search_query)
    id_call_string = searchresults_get_id(result, key)
    id_data = get_json(id_call_string)

    if len(id_data['results']) > 0: 
        
        movie_id = id_data["results"][0]["id"]
        poster_call_string = get_poster(movie_id, key)
        poster_data = get_json(poster_call_string)
        cast_call_string = searchresults_get_cast(movie_id, key)
        cast_data = get_json(cast_call_string)

        poster_path = poster_data["poster_path"]
        api_url = "https://image.tmdb.org/t/p/w600_and_h900_bestv2"
        poster_path = api_url + poster_path

        cast_members = []
        for i in range(len(cast_data["cast"])):
            cast_members.append(cast_data["cast"][i]["name"])

        return [poster_path, cast_members]
    
    else:
        return None

def searchresults_get_cast(id_num, key):
    id_num = str(id_num)
    api_request = "https://api.themoviedb.org/3/movie/movie_id/credits?api_key=&language=en-US"
    api_request = api_request.replace("movie_id", id_num)
    api_request = api_request.replace("api_key=", key)
    return api_request

def searchresults_get_id(movie, key):
    str = movie[0].strip()
    str = str.replace(" ", "%20")
    movie_query = "query="+str
    api_request = "https://api.themoviedb.org/3/search/movie?api_key=&language=en-US&query&page=1&include_adult=false"
    api_request = api_request.replace("query", movie_query)
    api_request = api_request.replace("api_key=", key)
    return api_request



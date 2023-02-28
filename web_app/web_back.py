from dotenv import load_dotenv
import base64
from requests import post, get
import json
import os
from geopy.geocoders import Nominatim
import folium
import pycountry


load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
geolocator = Nominatim(user_agent="my_name")

def get_token():
    '''
    This function returns client token
    '''
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode('utf-8')
    auth_base64 = str(base64.b64encode(auth_bytes), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic '+ auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    result = post(url, headers = headers, data = data)  # повертає json файл
    json_result = json.loads(result.content)
    token = json_result['access_token']
    return token


def get_auth_header(token:str):
    return {'Authorization': 'Bearer ' + token}


def search_for_artist_name(artist_name:str) -> str:
    '''
    This function returns id of an artist
    '''
    token = get_token()
    url = 'https://api.spotify.com/v1/search'
    headers = get_auth_header(token)
    query = f'?q={artist_name}&type=artist,track&limit=1'

    query_url = url + query
    result = get(query_url, headers = headers)
    json_result = json.loads(result.content)['artists']['items']
    if len(json_result) == 0:
        return None
    return json_result[0]['id']
# print(search_for_artist_name(get_token(), 'qwertyuiopsdfghjkl;cvbnm,.'))

def get_songs_by_artist(token:str, artist_id:str) -> list:
    '''
    This function returns list with all tracks of an artist
    '''
    url = f"https://api.spotify.com/v1/artists/{search_for_artist_name(artist_id)}/top-tracks?country=US"
    headers = get_auth_header(token)
    result = get(url, headers=headers)
    json_result = json.loads(result.content)['tracks']
    return json_result


def get_top_1_song_of_artist(artist_id:str) -> str:
    '''
    This function returns the most popular song of an artist
    '''
    token = get_token()
    songs = get_songs_by_artist(token, artist_id)
    res = []
    for idx, song in enumerate(songs):
        res.append((song['name'], song['popularity'], song))
    try:
        res = sorted(res, key = lambda x: x[1])[::-1][0]
        return res
    except IndexError:
        return None


def get_track_id(token:str, name:str) -> str:
    '''
    The function returns id of the most popular track
    '''
    popular_song = get_top_1_song_of_artist(token, name)[2]
    if 'uri' in popular_song:
        track_id = popular_song['uri']
    track_id = track_id.split(':')[2]
    return track_id


def get_markets(token:str, name:str) -> list:
    '''
    This is the main function in which the interaction with user is performed
    '''
    track_id = get_track_id(token, name)
    url = f"https://api.spotify.com/v1/tracks/{track_id}"
    headers = get_auth_header(token)

    result = get(url, headers=headers)
    json_result = json.loads(result.content)
    result = []
    markets = json_result['available_markets']
    for country in markets:
        try:
            coords = pycountry.countries.get(alpha_2=country)
            country_name = coords.name 
            result.append(country_name)
        except AttributeError:
            continue
    return result[:5]

def get_coords(phrase: str) -> list:
    """
    Returns the set of the letters found in a phrase
    """
    token = get_token()
    countries = get_markets(token, phrase)
    row = []
    for coords in countries:
        try:
            location = geolocator.geocode(coords, timeout=10) 
            row.append((coords, [location.latitude, location.longitude]))
        except AttributeError:
            continue
    return row




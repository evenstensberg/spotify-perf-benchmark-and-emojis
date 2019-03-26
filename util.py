import os
import requests
import json

base_uri = "https://api.spotify.com/"
headers = {
    "Content-Type": "application/json",
}

artifacts = []

# data collect
def save_dataset(data, filename):
    with open(filename, 'w') as data_set:  
        json.dump(data, data_set)

def get_endpoint(query):
    return base_uri + query

def set_auth_token():
    API_KEY = os.getenv("API_TOKEN")
    token = "Bearer " + API_KEY
    headers["Authorization"] = token


# audits
def get_playlist():
    url = get_endpoint("v1/me/playlists")
    resp = requests.get(url, headers=headers)
    return resp

def audit_playlist():
    playlist = get_playlist()
    save_dataset(playlist.json(), "dataset/playlist.json")
    playlist_t = playlist.elapsed.total_seconds()
    # TODO more metadata
    artifact = generate_artifact(playlist_t, 'playlist')
    save_artifact(artifact)

def audit_playlist_items():
   pass

def audit_playlist_convergence():
    pass

def audit_playlist_cache():
    pass

def audit_shared_cache():
    pass




# perf 
def initialize_audit():
    with open("perf/audit.json", 'w') as noop:
        json.dump([], noop)


def generate_artifact(stats, name):
    artifact = {
        'Req_t': stats,
        'id': name
    }
    return artifact

def save_artifact(artifact):
    artifacts.append(artifact)

def store_artifacts():
    with open("perf/audit.json", 'w') as data_set:
        json.dump(artifacts, data_set)


# fun

from random import randint

def get_json_file(file_path):
    with open(file_path) as fp:
        data = json.load(fp)
    return data

def create_playlist():
    emoji_l = get_json_file("fun/emojis.json")
    EMOJI_MAX_RANGE = len(emoji_l)
    random_n = randint(0, EMOJI_MAX_RANGE)
    playlist_name = emoji_l[random_n]['emoji']
    url = get_endpoint("v1/me/playlists")
    body = {
        "name": playlist_name,
        "public": True
    }
    resp = requests.post(url, headers=headers, json=body)
    return resp

def populate_from_existing_playlists():
    pass

def ():

import time
import os
import requests
import json
from pathlib import Path

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
    headers["Authorization"] = str(token)


def get_next(q):
    resp = requests.get(q, headers=headers)
    return resp

def add_songs(id, body):
        url = "https://api.spotify.com/v1/playlists/" + id + "/tracks"
        resp = requests.post(url, headers=headers, json=body)
        return resp
# audits
def get_playlist():
    url = get_endpoint("v1/me/playlists")
    resp = requests.get(url, headers=headers)
    return resp

def get_specified_playlist(id):
    url = get_endpoint("v1/playlists/" + id)
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

def create_playlist(override):
    emoji_l = get_json_file("fun/emojis.json")
    EMOJI_MAX_RANGE = len(emoji_l)
    random_n = randint(0, EMOJI_MAX_RANGE)
    playlist_name = emoji_l[random_n]['emoji']
    url = get_endpoint("v1/me/playlists")
    if override:
            playlist_name = override

    body = {
        "name": playlist_name,
        "public": True
    }
    resp = requests.post(url, headers=headers, json=body)
    return resp

def populate_from_existing_playlists():
    pass

def get_playlist_songs():
        playlists = get_playlist().json()
        save_dataset(playlists, "dataset/sets2.json")
        p_ids = []
        tot_list = []
        for i in playlists['items']:
                p_ids.append(i['id'])
        trecks = []
        abs_tracks = []
        for j in p_ids:
                p_list = get_specified_playlist(j).json()
                for q in p_list['tracks']['items']:
                        trecks.append(q['track']['uri'])
        while playlists['next']:
                resp = get_next(playlists['next']).json()
                new_pids = []
                for i in resp['items']:
                        new_pids.append(i['id'])
                for j in p_ids:
                        p_list = get_specified_playlist(j).json()
                        for q in p_list['tracks']['items']:
                                trecks.append(q['track']['uri'])
                save_dataset(playlists, "dataset/sets2.json")
                playlists['next'] = resp['next']
        save_dataset(playlists, "dataset/sets.json")
        return trecks

def merge_all(p_type):
        songs = get_playlist_songs()
        # todo quick maths divide and conquer
        chunk_norris = [songs[i:i + 100] for i in range(0, len(songs), 100)]
        chunkID = 0
        # generate chunked playlists w equal distribution
        if p_type is 'shuffle_board':
                for chunk in chunk_norris:
                        body = {
                                'uris': chunk
                        }
                        save_dataset(body, "debug/payload.shuffle-" + str(chunkID) + ".json")
                        new_plist_id = create_playlist().json()['id']
                        resp = add_songs(new_plist_id, body).json()
                        save_dataset(resp, "debug/snapshot.shuffle-" + str(chunkID) + ".json")
                        chunkID = chunkID + 1
        # one list
        if p_type is 'merge_all':
                new_plist_id = create_playlist(':)').json()['id']
                for chunk in chunk_norris:
                        body = {
                                'uris': chunk
                        }
                        save_dataset(body, "debug/payload.mergeall-" + str(chunkID) + ".json")
                        resp = add_songs(new_plist_id, body).json()
                        save_dataset(resp, "debug/snapshot.mergeall-" + str(chunkID) + ".json")
                        chunkID = chunkID + 1

def thank_you_next(shouldLoadDynamic=False):
        if shouldLoadDynamic is True:
                from dotenv import load_dotenv, find_dotenv
                load_dotenv(find_dotenv())
                set_auth_token()
        url = get_endpoint("v1/me/player/next")
        requests.post(url, headers=headers)
        return get_current_running()

def get_current_running():
        # concurrency <3
        time.sleep(5)
        url2 = get_endpoint("v1/me/player/currently-playing")
        return requests.get(url2, headers=headers).json()
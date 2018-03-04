from flask import Flask, render_template
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from flask import json
from flask import request
import pandas as pd
import math
#import pprint

# TODO: docker-ize
# TODO: add explanation, more tips on interactivity, genres list?, similar artists?, something about avg scores or area size, consistent artist????
# TODO: replace acoutinceess or instrumentalness (even work? check grimes...weird), with a tempo -> speed measure

def find_icon_img(images):
    if not images or len(images) == 0:
        return 'static/spotify.jpeg'
    for image in images:
        if image['width'] < 100:
            return image['url']
    return images[-1]['url']


def find_artist_img(images):
    if not images or len(images) == 0:
        return ''
    for image in images:
        if image['width'] < 500 and image['width'] > 100:
            return image['url']
    return images[-1]['url']


def convert_dB(x):
    """convert decibles (log scale) to range 0-1, setting arbitrary max at -50db"""
    x = abs(x)
    if x <= 1:
        return 0
    return math.log(x) / math.log(50)


def create_app():
    # instance relative looks for an instance folder
    app = Flask(__name__, instance_relative_config=True)

    # first load config.settings.py
    app.config.from_object('config.settings')
    # override config for prod from instance.config.py, silent allows it to be empty and not crash
    app.config.from_pyfile('settings.py', silent=True)
    client_id = app.config['CLIENT_ID']
    client_secret = app.config['CLIENT_SECRET']
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/_artist_search')
    def _artist_search():
        artist_search = request.args.get('q')
        artist_search = artist_search.replace('+', ' ') + '*'  # spotipy only works with spaces literal, '*' for wildcard
        artist_results = sp.search(q=artist_search, limit=5, offset=0, type='artist', market='US')
        results = [{'name': x['name'], 'uri': x['uri'], 'icon_img': find_icon_img(x['images']), 'artist_img': find_artist_img(x['images'])}
                   for x in artist_results['artists']['items']]
        #pp = pprint.PrettyPrinter(indent=4)
        #print '++  Ariist ++'*5
        #print pp.pprint(artist_results)
        return json.jsonify(matching_results=results)


    @app.route('/_audio_features_datacall', defaults={'artist_uri': 'spotify:artist:0asVlqTLu3TimnYVyY5Jxi'})
    @app.route('/_audio_features_datacall/<string:artist_uri>')
    def audio_features_datacall(artist_uri):
        top_tracks = sp.artist_top_tracks(artist_id=artist_uri, country='US')
        top_track_ids = {x['id']: x['name'] for x in top_tracks['tracks'][0:5]}
        featuresDF = pd.DataFrame(sp.audio_features(top_track_ids.keys()))
        featuresDF['name'] = featuresDF['id'].map(top_track_ids)
        featuresDF['loudness score'] = featuresDF['loudness'].apply(convert_dB)
        results = [] #[{'key':'song', 'values':[{'reason':'feature', 'device':'song', 'value':2}]
        for i, r in featuresDF.iterrows():
            item = dict()
            item['key'] = r['name']
            item['values'] = [{'device': r['name'], 'reason': k, 'value': v, 'uri':r['uri']}
                              for k, v in r[['acousticness', 'instrumentalness', 'danceability', 'energy', 'valence', 'loudness score']].to_dict().iteritems()]
            item['uri'] = r['uri']
            #if desired, ordered dict to control axis placement
            # item['values'] = [OrderedDict([('device', r['name']), ('reason', k), ('value', v)])
            #                   for k, v in r[['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness','valence']].to_dict().iteritems()]
            results.append(item)
        #pp = pprint.PrettyPrinter(indent=4)
        #print pp.pprint(results)
        return json.jsonify(features=results)

    return app

#app = create_app()
#app.run()
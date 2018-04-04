from flask import Flask, render_template
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy
from flask import json
from flask import request
import pandas as pd
import math

# TODO: add explanation, more tips on interactivity, genres list?, similar artists?, something about avg scores or area size, consistent artist????
# TODO: replace acoutinceess or instrumentalness (even work? check grimes...weird), with a tempo -> speed measure
# TODO: increase size of the chart itself, maybe just radius or decrease margins, for mobile mostly
# TODO: pull out radarchart as stand alone js file, call in other files


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
        if 100 < image['width'] < 500:
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

    def GetAudioFeaturesDF(artist_uri):
        top_tracks = sp.artist_top_tracks(artist_id=artist_uri, country='US')
        top_track_ids = {x['id']: x['name'] for x in top_tracks['tracks'][0:5]} #only top 5 tracks
        featuresDF = pd.DataFrame(sp.audio_features(top_track_ids.keys()))
        featuresDF['name'] = featuresDF['id'].map(top_track_ids)
        track_artists = [artist['name'] for artist in top_tracks['tracks'][0]['artists']]
        featuresDF['artist_name'] = ', '.join(track_artists)
        featuresDF['loudness score'] = featuresDF['loudness'].apply(convert_dB)
        return featuresDF

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/_artist_search')
    def _artist_search():
        artist_search = request.args.get('q')
        artist_search = artist_search.replace('+', ' ') + '*'  # spotipy only works with spaces literal, '*' for wildcard
        artist_results = sp.search(q=artist_search, limit=5, offset=0, type='artist', market='US')
        results = [
            {'name': x['name'], 'uri': x['uri'], 'icon_img': find_icon_img(x['images']), 'artist_img': find_artist_img(x['images'])}
                   for x in artist_results['artists']['items']
        ]
        return json.jsonify(matching_results=results)


    @app.route('/_audio_features_datacall', defaults={'artist_uri': 'spotify:artist:0asVlqTLu3TimnYVyY5Jxi'})
    @app.route('/_audio_features_datacall/<string:artist_uri>')
    #TODO : change this to use query params https://stackoverflow.com/questions/15182696/multiple-parameters-in-in-flask-approute
    def audio_features_datacall(artist_uri):
        results = []  # [{'key':'track', 'values':[{'reason':'feature', 'track':'song', 'value':2}]
        featuresDF = GetAudioFeaturesDF(artist_uri)
        for i, r in featuresDF.iterrows():
            item = dict()
            item['key'] = r['name']
            item['uri'] = r['uri']
            item['values'] = [{'track': r['name'], 'measure': k, 'value': v, 'uri':r['uri']}
                              for k, v in r[['acousticness', 'instrumentalness', 'danceability', 'energy', 'valence', 'loudness score']].to_dict().iteritems()]
            #if desired, ordered dict to control axis placement
            # item['values'] = [OrderedDict([('track', r['name']), ('measure', k), ('value', v)])
            #                   for k, v in r[['acousticness', 'danceability', 'energy', 'instrumentalness', 'liveness','valence']].to_dict().iteritems()]
            results.append(item)
        return json.jsonify(features=results)

    @app.route('/artist-compare')
    def artist_compare():
        return render_template('artist_compare.html')

    @app.route('/_audio_features_datacall_multi')
    # TODO: now need javascript to for index.html to call url, and artist_compare.html to call url_multi with proper artist uris...
    # TODO: check for the list value elements, if present make that call, if not make other????
    def audio_features_datacall_multi():
        #only take first 5 values
        #for each artist, call audio_features_datacall and then generate average scores
        artists_uris = request.args.get('artists_uris', None).split(',')[0:5]
        results = []  # [{'key':'artist', 'values':[{'reason':'feature', 'track':'artist', 'value':2}]
        for artist_uri in artists_uris:
            print(artist_uri)
            featuresDF = GetAudioFeaturesDF(artist_uri)
            artist_name = featuresDF['artist_name'][0]
            feature_names = ['acousticness', 'instrumentalness', 'danceability', 'energy', 'valence', 'loudness score']
            result = {'key': artist_name, 'uri': artist_uri, 'values': []}
            values = [{'measure': feature, 'track': artist_name, 'uri' : artist_uri, 'value': featuresDF[feature].mean()}
                      for feature in feature_names]
            print values
            result['values'] = values
            results.append(result)
        return json.jsonify(features=results)

    return app

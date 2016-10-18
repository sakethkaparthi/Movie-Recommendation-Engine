from flask import Flask
from flask import render_template
from databaseMethods import *
from pymongo import MongoClient
import sqlite3
import requests

app = Flask(__name__)
client = MongoClient('localhost', 27017)
conn = sqlite3.connect('recommendation_engine.db')
db = client['movies-db']
movies = db["movies"]

p = getPopularMovies(conn, 50)
ids = []
popular = []
param = {'api_key': "d4dc650ab1e0ee61a3a4e17453f770f5"}
info_link = "https://api.themoviedb.org/3/movie/"
poster_path = "https://image.tmdb.org/t/p/w185"
imdb_link = "http://www.imdb.com/title/{id}/"

for i in range(len(p)):
    m = list(p[i])
    id = getTmdbId(conn, m[0])
    id = int(float((str(id[0])[1:-2])))
    movie = movies.find_one({"id": id})
    if not movie:
        r = requests.get(info_link + str(id), params=param)
        data = r.json()
        movie = {"id": id, "name": data['original_title'], "overview": data['overview'],
                 "poster": str(poster_path + data['poster_path']),
                 "imdb": imdb_link.format(id=data["imdb_id"])}
        movies.insert_one(movie)
    print movie
    popular.append(movie)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/popular_movies')
def popularmovies():
    return render_template('movies.html', movies=popular)


@app.route('/highest_rated')
def highestratedmovies():
    return render_template('movies.html')


if __name__ == '__main__':
    app.run()

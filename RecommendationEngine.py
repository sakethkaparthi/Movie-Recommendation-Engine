from flask import Flask
from flask import render_template
import sqlite3
from databaseMethods import *
import requests

app = Flask(__name__)

conn = sqlite3.connect('recommendation_engine.db')
p = getPopularMovies(conn, 10)
ids = []
popular = []
param = {'api_key': "d4dc650ab1e0ee61a3a4e17453f770f5"}
info_link = "https://api.themoviedb.org/3/movie/"
poster_path = "https://image.tmdb.org/t/p/w185"

for i in range(len(p)):
    m = list(p[i])
    id = getTmdbId(conn, m[0])
    id = int(float((str(id[0])[1:-2])))
    r = requests.get(info_link + str(id), params=param)
    data = r.json()
    movie = {"name": data['original_title'], "overview": data['overview'],
             "poster": str(poster_path + data['poster_path'])}
    print movie
    popular.append(movie)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/popular_movies')
def popularmovies():
    return render_template('popularmovies.html', movies=popular)


if __name__ == '__main__':
    app.run()

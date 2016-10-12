from flask import Flask
from flask import render_template
import sqlite3
from databaseMethods import *

app = Flask(__name__)

conn = sqlite3.connect('recommendation_engine.db')
popular = getPopularMovies(conn, 20)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/popular_movies')
def popularmovies():
    return render_template('popularmovies.html', movies=popular)


if __name__ == '__main__':
    app.run()

#!flask/bin/python

from flask import Flask
from flask import render_template, flash, request, url_for, redirect, session
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from databaseMethods import *
from forms import *
from dbtest import *
from pymongo import MongoClient
import sqlite3
import requests
import time

app = Flask(__name__)
app.config.from_object('config')
client = MongoClient('localhost', 27017)
conn = sqlite3.connect('recommendation_engine.db')
db = client['movies-db']
movies = db["movies"]

conn.execute("""CREATE TABLE IF NOT EXISTS users
(id INTEGER PRIMARY KEY,
username VARCHAR(25) UNIQUE NOT NULL,
email VARCHAR(35) NOT NULL,
password VARCHAR(255) NOT NULL)""")
conn.commit()

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
                 "rating": m[2],
                 "imdb": imdb_link.format(id=data["imdb_id"])}
        movies.insert_one(movie)
    # print movie
    popular.append(movie)

"""session['logged-in'] = False
session['username'] = ''"""


@app.route('/home')
@app.route('/')
def home():
    print 'username' in session
    return render_template('home.html', session=session)


@app.route('/logout')
def logout():
    session['logged-in'] = False
    session['username'] = ''
    return redirect(url_for('home'))


@app.route('/popular_movies/')
def popularmovies():
    session['popular'] = True
    return render_template('movies.html', movies=popular)


@app.route('/highest_rated')
def selectRatings():
    return render_template('minimumratings.html')


@app.route('/highest_rated/<int:number>')
def highestratedMovies(number):
    print "Here"
    session['popular'] = False
    rated = getHighestRatedMovies(conn, number, 10)
    print rated
    highest = []
    for j in range(len(rated)):
        m2 = list(rated[j])
        id2 = getTmdbId(conn, m2[0])
        id2 = int(float((str(id2[0])[1:-2])))
        print id2
        movie2 = movies.find_one({"id": id2})
        if not movie2:
            resp = requests.get(info_link + str(id2), params=param)
            data2 = resp.json()
            # print data2
            movie2 = {"id": id2, "name": data2['original_title'], "overview": data2['overview'],
                      "poster": str(poster_path + data2['poster_path']),
                      "rating": m2[2],
                      "imdb": imdb_link.format(id=data2["imdb_id"])}
            movies.insert_one(movie2)
        # print movie2
        highest.append(movie2)
    return render_template('movies.html', movies=highest)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    try:
        form = SignUpForm(request.form)
        # print(form.errors())
        if form.validate_on_submit():
            print 'Hello'
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            existing_users = conn.execute("SELECT * FROM users WHERE username = ?", [username]).fetchall()
            if len(existing_users) > 0:
                flash("That username is already taken")
                return render_template('signup.html', form=form)
            else:
                conn.execute("INSERT INTO users(username, email, password) VALUES(?,?,?)", [username, email, password])
                flash("Thank you for signing up")
                session['logged-in'] = True
                session['username'] = username
                conn.commit()
                return redirect(url_for('home'))
        return render_template('signup.html', form=form)
    except Exception as e:
        print(str(e))
        return (str(e))


@app.route('/login', methods=['GET', 'POST'])
def login():
    try:
        form = LoginForm(request.form)
        error = ''
        if form.validate_on_submit():
            data = conn.execute("SELECT * FROM users WHERE username = ?", [form.username.data]).fetchall()
            data = data[0][3]
            if sha256_crypt.verify(form.password.data, data):
                session['logged-in'] = True
                session['username'] = form.username.data
                flash('You are now logged in')
                return redirect(url_for('home'))
            else:
                error = 'Invalid credentials. Please try again.'
        return render_template('login.html', form=form, error=error)
    except Exception as e:
        print(str(e))
        error = 'Invalid credentials. Please try again.'
        return render_template('login.html', form=form, error=error)


def nameToInt(username):
    return str(int(''.join([str(ord(x)) for x in list(username)])))[0::4]


@app.route('/rate', methods=['GET', 'POST'])
def rate():
    if request.method == 'POST':
        username = request.form['username']
        movieId = request.form['id']
        rating = request.form['rating']
        addRating(conn, nameToInt(username), str(movieId), str(rating), str(int(time.time())))
    elif request.method == 'GET':
        pass


@app.route('/user')
def user_page():
    if 'username' not in session.keys() or session['username'] == '':
        error = "Please login"
        return render_template('user.html', error=error)
    else:
        user_rated_movies = getUserRatings(conn, nameToInt(session['username']))
        user_movies = []
        for k in range(len(user_rated_movies)):
            try:
                mo = list(user_rated_movies[k])
                mid = mo[0]
                movieu = movies.find_one({"uid": mid})
                if not movieu:
                    ru = requests.get(info_link + str(mid), params=param)
                    datau = ru.json()
                    movieu = {"uid": mid, "name": datau['original_title'], "overview": datau['overview'],
                              "poster": str(poster_path + datau['poster_path']),
                              "rating": mo[1],
                              "imdb": imdb_link.format(id=datau["imdb_id"])}
                    movies.insert_one(movieu)
                # print movie
                user_movies.append(movieu)
            except:
                pass

        recommended_movies = []
        p = getUserRecommendations(nameToInt(session['username']), conn)
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
                         "rating": (data['vote_average'] / 2),
                         "imdb": imdb_link.format(id=data["imdb_id"])}
                movies.insert_one(movie)
            print movie
            recommended_movies.append(movie)

    return render_template('user.html', error='', umovies=user_movies, movies=recommended_movies)


if __name__ == '__main__':
    app.run()

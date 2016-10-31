#!flask/bin/python

from flask import Flask
from flask import render_template, flash, request, url_for, redirect, session
from wtforms import Form, BooleanField, StringField, PasswordField, validators
from passlib.hash import sha256_crypt
from databaseMethods import *
from forms import *
from pymongo import MongoClient
import sqlite3
import requests

app = Flask(__name__)
app.config.from_object('config')
client = MongoClient('localhost', 27017)
conn = sqlite3.connect('recommendation_engine.db')
db = client['movies-db']
movies = db["movies"]

conn.execute("""create table if not exists users
(id integer primary key,
username varchar(25) unique not null,
email varchar(35) not null,
password varchar(255) not null)""")
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
                 "imdb": imdb_link.format(id=data["imdb_id"])}
        movies.insert_one(movie)
    print movie
    popular.append(movie)

session = {'logged-in':False, 'username':''}

@app.route('/home')
@app.route('/')
def home():
    print session['username']
    return render_template('home.html',session=session)

@app.route('/logout')
def logout():
    session['logged-in'] = False
    session['username'] = ''
    return redirect(url_for('home'))

@app.route('/popular_movies')
def popularmovies():
    return render_template('movies.html', movies=popular)


@app.route('/highest_rated')
def selectRatings():
    return render_template('minimumratings.html')


@app.route('/highest_rated/<int:number>')
def highestratedMovies(number):
    r = getHighestRatedMovies(conn, number, 10)
    highest = []
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
        highest.append(movie)
    return render_template('movies.html', movies=highest)

@app.route('/signup', methods=['GET','POST'])
def signup():
    try:
        form = SignUpForm(request.form)
        #print(form.errors())
        if form.validate_on_submit():
            print 'Hello'
            username = form.username.data
            email = form.email.data
            password = sha256_crypt.encrypt((str(form.password.data)))
            existing_users = conn.execute("select * from users where username = ?",[username]).fetchall()
            if len(existing_users) > 0:
                flash("That username is already taken")
                return render_template('signup.html',form=form)
            else:
                conn.execute("insert into users(username, email, password) VALUES(?,?,?)",[username,email,password])
                flash("Thank you for signing up")
                session['logged-in'] = True
                session['username'] = username
                conn.commit()
                return redirect(url_for('home'))
        return render_template('signup.html',form=form)
    except Exception as e:
        print(str(e))
        return(str(e))

@app.route('/login', methods=['GET','POST'])
def login():
    try:
        form = LoginForm(request.form)
        error = ''
        if form.validate_on_submit():
            data = conn.execute("select * from users where username = ?",[form.username.data]).fetchall()
            data = data[0][3]
            if sha256_crypt.verify(form.password.data, data):
                session['logged-in'] = True
                session['username'] = form.username.data
                flash('You are now logged in')
                return redirect(url_for('home'))
            else:
                error = 'Invalid credentials. Please try again.'
        return render_template('login.html',form=form,error=error)
    except Exception as e:
        print(str(e))
        error = 'Invalid credentials. Please try again.'
        return render_template('login.html',form=form,error=error)

if __name__ == '__main__':
    app.run()

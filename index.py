import sqlite3
from databaseMethods import *
conn = sqlite3.connect('recommendation_engine.db')

print getPopularMovies(conn,10)
print getHighestRatedMovies(conn,100,10)

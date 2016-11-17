from pymongo import MongoClient

client = MongoClient('localhost', 27017)
db = client['movies-db']
movies = db["movies"]


def getPopularMovies(conn, limit):
    return conn.execute("""select movies.movieId,title,avg(rating) as rate,count(rating) as cnt from movies
	inner join ratings on movies.movieId = ratings.movieId
    group by movies.movieId
    order by cnt desc
    limit """ + str(limit) + ";").fetchall()


def getHighestRatedMovies(conn, mini, limit):
    return conn.execute("""select movies.movieId,title,avg(rating) as rate,count(rating) as cnt from movies
	inner join ratings on movies.movieId = ratings.movieId
	group by movies.movieId
	having cnt > """ + str(mini) + """
	order by rate desc
	limit """ + str(limit) + ";").fetchall()


def getTmdbId(conn, id):
    return conn.execute("select tmdbId from links where movieId=" + str(id)).fetchall()


def getTmdbIds(conn, id):
    return conn.execute("select tmdbId from links")


def getRandomMovies(conn, cnt, limit):
    return conn.execute("""select movies.movieId,title,genres,avg(rating) as rate,count(rating) as cnt from movies
	inner join ratings on movies.movieId = ratings.movieId
    group by movies.movieId
    having cnt > """ + str(cnt) + """
    order by random()
    limit """ + str(limit) + ";").fetchall()


def getUserIds(conn):
    return conn.execute("""select distinct userId
    from ratings""").fetchall()


def getUserRatings(conn, userId):
    return conn.execute("""select DISTINCT movieId,rating
    from ratings
    where userId = """ + str(userId)).fetchall()


def addRating(conn, userId, movieId, rating, time):
    cursor = conn.execute("select * from ratings where userId = " + userId + " and movieId =" + movieId).fetchall()
    if len(cursor) > 0:
        conn.execute("update ratings set rating = " + rating
                     + ",timestamp = " + time
                     + " where userId =" + userId
                     + " and movieId = " + movieId + ";")
        conn.commit()
        result = movies.update_one({'uid': int(movieId)}, {'$set': {'rating': float(rating) }})
        print result.matched_count, result.modified_count
    else:
        conn.execute("insert into ratings VALUES(" + userId
                     + "," + movieId + ","
                     + rating + "," + time + ");")
        conn.commit()


def getTitlefromId(conn, movieId):
    return conn.execute("""select title
		from movies 
		where movieId = """ + str(movieId)).fetchall()

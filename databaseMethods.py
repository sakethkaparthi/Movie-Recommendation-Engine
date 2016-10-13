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

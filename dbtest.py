import sqlite3
from databaseMethods import *
from computations import *

conn = sqlite3.connect('recommendation_engine.db')

movieList = getRandomMovies(conn,200,15)
for movie in movieList:
	print movie[1]

conn.execute("drop table if exists users")
conn.commit()

'''userlist = conn.execute("""select username from users""").fetchall()
if(len(userlist)>0):
	for user in userlist:
		print user
	input()'''

ratingsDict = {}
userIds = [str(i)[1:-2] for i in getUserIds(conn)]

for userId in userIds:
    ratingsDict[str(userId)] = dict(getUserRatings(conn,userId))

ratingsDict['New User'] = dict([(movie[0],float("{0:.1f}".format(movie[3]))) for movie in movieList])

print 'User ratings map created'

recommendations = userRecommendations('New User',ratingsDict)

for recommendation in recommendations:
	if recommendation[1] < 5:
		break
	print getTitlefromId(conn,recommendation[0]),recommendation[1]

'''
for userId in userIds:
    print getUserRatings(conn,userId)'''

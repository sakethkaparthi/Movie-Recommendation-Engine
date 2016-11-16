import sqlite3

from databaseMethods import *
from computations import *


def getUserRecommendations(userid, conn):

    movieList = getUserRatings(conn,userid)
    for movie in movieList:
        print movie[0],movie[1]

    '''conn.execute("drop table if exists users")
    conn.commit()
    '''

    '''userlist = conn.execute("""select username from users""").fetchall()
    if(len(userlist)>0):
        for user in userlist:
            print user
        input()'''

    ratingsDict = {}
    userIds = [str(i)[1:-2] for i in getUserIds(conn)]

    for userId in userIds:
        ratingsDict[str(userId)] = dict(getUserRatings(conn, userId))

    ratingsDict[userid] = dict([(movie[0], float("{0:.1f}".format(movie[1]))) for movie in movieList])
    print ratingsDict[userid]
    print 'User ratings map created'

    recommendations = userRecommendations(userid, ratingsDict)

    '''for recommendation in recommendations[0:20]:
        if recommendation[1] < 5:
            break
        #print getTitlefromId(conn, recommendation[0]), recommendation[1]
        print recommendation'''
    return recommendations[0:20]

    '''
    for userId in userIds:
        print getUserRatings(conn,userId)'''

if __name__ == '__main__':
    #userid = raw_input("Enter the user id")
    conn = sqlite3.connect('recommendation_engine.db')
    #getUserRecommendations(userid,conn)

    cursor = conn.execute("SELECT sql FROM sqlite_master WHERE tbl_name='ratings' AND type='table'")
    for col in cursor:
        print col
    #input()
    cursor = conn.execute("SELECT * FROM ratings ORDER BY timestamp")
    for row in cursor:
        print row
    #conn.execute("DELETE FROM ratings WHERE timestamp > 1452404919;")
    conn.commit()
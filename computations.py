from math import sqrt


def pearsonCorrelation(person1, person2, ratingsDict):
    both_rated = {}
    for item in ratingsDict[person1]:
        if item in ratingsDict[person2]:
            both_rated[item] = 1

    if len(both_rated) == 0:
        return 0

    person1_preferences_sum = sum([ratingsDict[person1][item] for item in both_rated])
    person2_preferences_sum = sum([ratingsDict[person2][item] for item in both_rated])

    person1_square_preferences_sum = sum([pow(ratingsDict[person1][item], 2) for item in both_rated])
    person2_square_preferences_sum = sum([pow(ratingsDict[person2][item], 2) for item in both_rated])

    product_sum_of_both_users = sum([ratingsDict[person1][item] * ratingsDict[person2][item] for item in both_rated])

    num_value = product_sum_of_both_users - (person1_preferences_sum * person2_preferences_sum) / len(both_rated)
    try:
        den_value = sqrt((person1_square_preferences_sum - pow(person1_preferences_sum, 2) / len(both_rated)) *
                         (person2_square_preferences_sum - pow(person2_preferences_sum, 2) / len(both_rated)))
    except:
        print "Exception"
        print person1_preferences_sum, person1_square_preferences_sum, person2_preferences_sum, person2_square_preferences_sum
        pass
    if den_value == 0:
        return 0
    else:
        score = num_value / den_value
        return score


def similarUsers(person, userIds, ratingsDict):
    similarUserDict = {}
    for userId in userIds:
        score = pearsonCorrelation(person, userId, ratingsDict)
        if score > 0:
            similarUserDict[str(userId)] = float("{0:.4f}".format(score))

    similarUserDict = sorted(similarUserDict.iteritems(), key=lambda (k, v): (v, k), reverse=True)
    return similarUserDict


def userRecommendations(person, ratingsDict):
    totals = {}
    simSums = {}
    rankings_list = []

    for other in ratingsDict:
        if other == person:
            continue
        sim = pearsonCorrelation(person, other, ratingsDict)

        if sim <= 0.5:
            continue
        for item in ratingsDict[other]:
            if item not in ratingsDict[person] or ratingsDict[person][item] == 0:
                totals.setdefault(item, 0)
                totals[item] += ratingsDict[other][item] * sim
                simSums.setdefault(item, 0)
                simSums[item] += sim

    rankings = [(total / simSums[item], item) for item, total in totals.items()]
    rankings.sort()
    rankings.reverse()
    recommendations_list = [(recommendations_item, score) for score, recommendations_item in rankings]
    return recommendations_list

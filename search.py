from datetime import datetime
from elasticsearch import Elasticsearch
import os
es = Elasticsearch()
profile = dict()
res = dict()

userID = 129    # hardcoded userID (Can be modified to pull it from input/file/somewhere
DECAY_FACTOR = -0.15 # factor which controls freshness of results(how much each result should lose in value)
AUTHOR_WEIGHT = 1.3 # how much the fact that the same author has been clicked on before should impact the search
RETURNED_RESULTS = 10000 # how many results ES should return
HISTORY_LIMIT = 5 # How many previous results we keep in history and use to modify the search


def addHistory(query, index):
    # add search history to profile
    profile['_source']['searchHistory'].append(query)
    if (len(profile['_source']['searchHistory']) >= 5):
        profile['_source']['searchHistory'].pop

    if index != None:
    # add clicked result to profile
        profile['_source']['selectedRes'].append( { "author": res['hits']['hits'][index]['_source']['author'] } )
        while (len(profile['_source']['selectedRes']) >= HISTORY_LIMIT):
            profile['_source']['selectedRes'].pop # if we have more than the allowed number of results, remove the first one(s)

    updatedProfile = {
            "doc": {
                "searchHistory" : profile["_source"]["searchHistory"],
                "selectedRes"   : profile["_source"]["selectedRes"]
                }
            }
#update the user index with the modified profile
    es.update(index="user", doc_type='profile', id=userID, body=updatedProfile)

def RepresentsInt(s):
    try:
        int(s)
        return True
    except ValueError:
        return False



# Comparator to sort returned documents by score after modifying the score locally
def cmp_items(a, b):
        if a['_score'] < b['_score']:
            return 1
        elif a['_score'] == b['_score']:
            return 0
        else:
            return -1


# Create a profile if we have a new user
# upsert: if document doesn't exist. Create one with the following data
updatedProfile = {
       "doc": {
            },
        "upsert": {
                "searchHistory": list(),
                "selectedRes": list()
            }
        }

es.update(index="user", doc_type='profile', id=userID, body=updatedProfile)


# Search
while True:
    profile = es.get(index="user", doc_type="profile", id=userID)
    print profile


    print "Enter a query term:"
    query = raw_input()

    res = es.search(index="twitter", body={"query": {"query_string": {'query': query}}, 'size': RETURNED_RESULTS})
    print("Got %d Hits:" % res['hits']['total'])
    resMap = dict()
    authorMap = dict()

# create hashmaps in order to speed up the later parts where we augment the scores
    maxScore = res['hits']['max_score']
    for hit in res['hits']['hits']:
        hit['_score'] = hit['_score'] / maxScore    # Normalize the scores so they are floats [0,1]
        resMap[hit['_id']] = hit                    # Dictionary (docID,hit)
        authorMap[hit['_source']['author']] = hit   # Dictionary (author, hit)

# weight results if a previous search returned the same docID
    resCount = 1 # counter for weighting results by freshness
    for histTerm in profile['_source']['searchHistory']:
        histRes = es.search(index="twitter", body={"query": {"query_string": {'query': histTerm}}, 'size': RETURNED_RESULTS})
        histMaxScore = histRes['hits']['max_score'] # Max score for these results
        for histHit in histRes['hits']['hits']:
            if histHit['_id'] in resMap:    # check if this result exists in our original search
                histHitScore = histHit['_score']
                histHitScore = histHitScore/histMaxScore   # normalize the score to be in range [0,1]
                histHitScore = (1 - (resCount * DECAY_FACTOR)) * histHitScore # decay the score by freshness
                resMap[histHit['_id']]['_score']+= histHitScore # add the score to our originals' hit score
        resCount+=1

# weight results if it contains an author previously clicked on
    for selRes in profile['_source']['selectedRes']:
        clickedAuthor = selRes['author']
        if clickedAuthor in authorMap:
            authorMap[clickedAuthor]['_score'] *= AUTHOR_WEIGHT # Scale original score if the author has previously been clicked on

    # resort items after modifying score
    res['hits']['hits'].sort(cmp_items)

    # present results to user
    i = 0;
    limit = 10
    newSearch = False
    for hit in res['hits']['hits']:
        print(str(i) + ": %(author)s: ---------- %(text)s\n" % hit["_source"])
        print("-- Score: " + str(hit["_score"]))
        i+=1
        endLoop = False
        if i >= limit or i == len(res['hits']['hits']):
            while True:
                numResults = len(res['hits']['hits']) - i
                if numResults > 10:
                    numResults = 10
                print "show ne(x)t "+ str(numResults) +" results, pick a result 0-" + str(i-1) + " or make a new (s)earch"
                ans = raw_input()
                if ans == "x":
                    limit += 10
                    break
                elif ans == "s":
                    endLoop = True
                    newSearch = True
                    break
                elif RepresentsInt(ans):
                    endLoop = True
                    index = int(ans)
                    break
                else:
                    continue
        if endLoop:
            break
    if newSearch:
        addHistory(query, None) # If the user wants to keep searching without picking a result. Add their search query to their profile.
        continue




    print "\n\n"
    print res['hits']['hits'][index]['_source']['text']
    while True:
        print "\nDo you want to visit this tweet on www.twitter.com?, y/n"
        inp = raw_input()
        if inp == "y":
            bashCommand = "xdg-open http://twitter.com/anyuser/status/" + str(res["hits"]["hits"][index]["_id"]) # This works for Ubuntu 17.10 atleast. Should probably be replaced with something more OS-agnostic
            os.system(bashCommand)
            break
        elif inp == "n":
            break

    # add search history to profile
    addHistory(query, index)



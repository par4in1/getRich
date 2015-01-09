from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from operator import add
import datetime
import plutchik
import pymongo

def dateTimeAndPlutchik(tweet):
    try:
        date = datetime.datetime.strptime(tweet[0], '%a %b %d %H:%M:%S +0000 %Y')
        key = str(date.month) + "/" + str(date.day)
        tweetMoods = plutchik.executeTweet(tweet[1])
        return key, tweetMoods
    except:
        print "not a date"


def retrieve(t):
    client = pymongo.MongoClient('giedomak.nl')
    db = client.test_database
    tweets = db.tweets
    return tweets.find_one(None, None, t)

def split_tweet(t):
    result = t.split(';',1)
    result.extend([""])
    return result


logFile = "C:\spark-1.2.0-bin-hadoop2.4/README.md"  # Should be some file on your system
sc = SparkContext("local[4]", "GetRich")
ssc = StreamingContext(sc, 1)

stream = ssc.socketTextStream("localhost", 9999)
tweetData = stream.flatMap(lambda line: line.split("\r\n"))
# tweetData.pprint()

#tweetData = sc.textFile(logFile).cache()
# tweetData = sc.parallelize([
#         {"created_at": "Mon Jan 05 01:05:03 +0000 2010", "text":"http://"},
#         {"created_at": "Mon Jan 06 01:05:03 +0000 2010", "text":"blub RT"},
#         {"created_at": "Mon Jan 08 01:05:03 +0000 2010", "text":"Guido RT zit naast mij"},
#         {"created_at": "Mon Jan 08 01:05:03 +0000 2010", "text":"blubsa"},
#         {"created_at": "Mon Jan 08 01:05:03 +0000 2010", "text":"RT Ik heb lol"},
#         {"created_at": "Mon Jan 08 01:05:03 +0000 2010", "text":"RT Ik heb lol en boos"},
#         {"created_at": "Mon Jan 08 01:05:03 +0000 2010", "text":"RT Haat klote kut"},
#     ])

# client = pymongo.MongoClient('giedomak.nl')
# db = client.test_database
# tweets = db.tweets

# tweetdata = range(100)
# tweetdata = sc.parallelize(tweetdata)

#tweetdata = tweetdata.map(lambda t: tweets.find_one(None, None, t))
# tweetdata = tweetdata.map(retrieve)

# print tweetdata.collect()

tweetData = tweetData.map(split_tweet)
# tweetData.pprint()
# tweetData = tweetData.map(lambda s: (s[0], ''.join(str(x) for x in s[1:])))
# tweetData.pprint()
tweetData = tweetData.filter(lambda t: not("http" in t[1]) and "RT" in t[1])
# tweetData = tweetData.filter(lambda t: not("http" in t[1]) and "RT" in t[1])
# tweetData = tweetData.filter(lambda t: "RT" in t[1:])
# tweetData.pprint()

moodData = tweetData.map(dateTimeAndPlutchik)
# moodData.pprint()
moodData = moodData.filter(lambda t: not all(m == 0 for m in t[1]))
# moodData.pprint()
# print moodData.pprint()

# moodData.pprint()

moodTotal = moodData.reduceByKey(lambda a, b: map(add, a, b))
# moodCount = moodData.countByKey()     # No count in streaming API

# moodDay = map(lambda a: (a[0], map(lambda b: b/moodCount[a[0]], a[1])), moodTotal.pprint())

moodTotal.pprint()
# moodCount.pprint()
# moodDay.pprint()

ssc.start()             # Start the computation
ssc.awaitTermination()  # Wait for the computation to terminate

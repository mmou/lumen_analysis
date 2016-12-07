"""

1) How many accounts receive more than 1 notice?

total accounts:
>>> len(screen_names_to_notice_timestamps)
31899

total accounts with more than 1 notice:
>>> len([x for x in screen_names_to_notice_timestamps if len(screen_names_to_notice_timestamps[x])>1])
12111

>>> print("duplicate_accounts: {0}".format(duplicate_accounts))
duplicate_accounts: 13211
>>> len(retrieved_tweets_v2)
31899

So 1/3 of accounts get more than 1 notice. TODO: distribution??

>>> len(screen_names_to_num_notices)
31899
>>> len([x for x in screen_names_to_num_notices if screen_names_to_num_notices[x]==1])
19788

>>> len(tweets)
19785
>>> len(tweets_multiple_notices)
12106


2) How many accounts are suspended?
>>> print("total_accounts: {0}".format(total_accounts))
total_accounts: 706
>>> print("not_enough_data_accounts: {0}".format(not_enough_data_accounts))
not_enough_data_accounts: 195
>>> print("suspended_accounts: {0}".format(suspended_accounts))
suspended_accounts: 0
>>> print("enough_and_suspended: {0}".format(enough_and_suspended))
enough_and_suspended: 0

3) How may accounts have enough data

3) Study focusing on accounts that received only 1 notice and are not suspended


"""

import twitter
import datetime
api = twitter.Api(consumer_key="",
                  consumer_secret="",
                  access_token_key="",
                  access_token_secret="")

##############

# from file of screennames in DMCA notices to twitter, get notices, screen_names_to_notice_timestamps

path = "./output/twitter_notices_080116-112116.csv"


def get_notices_and_screen_names(path):
    notices = {} # notices[id] = {timestamp: 1, screen_names: []}
    all_screen_names = {} # screen_names[name] = [timestamps]
    with open(path, 'r') as f:
        lines = f.readlines()
    for i in range(len(lines)):
        line = lines[i]
        cells = line.split(",")
        cells[-1] = cells[-1].replace("\n","")
        id = cells[0]
        timestamp = cells[1]
        screen_names = [cell for cell in cells[2:] if len(cell) > 0]
        notices[id] = {"timestamp": timestamp, "screen_names": screen_names}
        for name in screen_names:
            if name not in all_screen_names:
                all_screen_names[name] = []
            all_screen_names[name].append(timestamp)
    return notices, all_screen_names

notices, screen_names_to_notice_timestamps = get_notices_and_screen_names(path)

output_path = "screen_names_to_notice_timestamps_080116-112116.csv"
labels = ["screen_name", "notice_timestamp"]
rows = []
rows.append(",".join(labels))
for name in screen_names_to_notice_timestamps:
    for timestamp in screen_names_to_notice_timestamps[name]:
        row = [name, timestamp]
        rows.append(",".join(row))
with open(output_path, 'w') as f:
    f.write("\n".join(rows))


#################################

# refinding out how many screen_names are there, and how many of them only have 1 notice
screen_names_to_num_notices = {}
with open("screen_names_to_notice_timestamps_080116-112116.csv") as f:
    lines = f.readlines()
for line in lines[1:]:
    cells = line.split(",")
    screen_name = cells[0]
    if screen_name not in screen_names_to_num_notices:
        screen_names_to_num_notices[screen_name] = 0
    screen_names_to_num_notices[screen_name] += 1

len(screen_names_to_num_notices)
len([x for x in screen_names_to_num_notices if screen_names_to_num_notices[x]==1])


##################################

# with notices object, get tweet times for each account in each notice: twitter_notices_accounts_tweet_times_
# filter: do not include accounts that received more than 1 notice

def get_tweet_times(screen_name): #, timestamp, days_range):
    max_id = None
    tweet_times = []
    try:
        while True:
            #print("screen_name: {0}: at id {1}; {2} tweets".format(screen_name, max_id, len(tweet_times)))
            statuses = api.GetUserTimeline(screen_name=screen_name, count=200, max_id=max_id)
            this_tweet_times = [s.created_at_in_seconds for s in statuses if s.id is not max_id]
            if len(this_tweet_times) == 0:
                break
            tweet_times += this_tweet_times
            if max_id is None or statuses[-1].id < max_id:
                max_id = statuses[-1].id
            else:
                break
    except:
        return ["SUSPENDED!"]
    if len(tweet_times) > 0:
        print("STOPPED at post id {0}, total number {1} tweets, earliest time {2}; account name: {3}".format(
        max_id, len(tweet_times), datetime.datetime.utcfromtimestamp(tweet_times[-1]), screen_name))
    else:
        print("STOPPED at post id {0}, total number {1} tweets, earliest time {2}; account name: {3}".format(
        max_id, len(tweet_times), -1, screen_name))
    return tweet_times

def get_tweets(notices):
    retrieved_tweets = {}   # retrieved_tweets[screen_name] = []
    for id in notices.keys():
        for screen_name in notices[id]["screen_names"]:
            if screen_name in retrieved_tweets:
                print("already saw {0} !!!".format(screen_name))
            else:
                retrieved_tweets[screen_name] = get_tweet_times(screen_name)
    return retrieved_tweets


output_path = "twitter_notices_accounts_tweet_times_080116-112116.csv"
#output_max_path = "twitter_notices_accounts_tweet_times_max_080116-112116.csv"

epoch = datetime.datetime.utcfromtimestamp(0)

labels = ["notice_id", "notice_timestamp", "screen_name", "num_notices", "is_suspended", "tweet_timestamp"]
with open(output_path, 'w') as f:
    f.write(",".join(labels))
with open(output_max_path, 'w') as f:
    f.write(",".join(labels))    

retrieved_tweets = {}   # retrieved_tweets[screen_name] = []
for id in notices.keys():
    notice_rows = []
    notice_datetime_timestamp = datetime.datetime.strptime(notices[id]["timestamp"], "%Y-%m-%dT%H:%M:%SZ") # 2016-11-27T23:51:56Z
    notice_seconds = (notice_datetime_timestamp - epoch).total_seconds()
    for screen_name in notices[id]["screen_names"]:
        is_suspended = False
        num_notices = len(screen_names_to_notice_timestamps[screen_name])
        if screen_name in retrieved_tweets:
            # FILTER OUT: do not include repeated screen_names
            print("duplicate screen name: {0} !!!".format(screen_name))
        else:
            retrieved_tweets[screen_name] = []
            retrieved_tweets[screen_name] = get_tweet_times(screen_name)
            if (retrieved_tweets[screen_name]) == ["SUSPENDED!"]:
                is_suspended = True
                row = [id, notice_seconds, screen_name, num_notices, is_suspended, ""]
            else:
                for time in retrieved_tweets[screen_name]:
                    row = [id, notice_seconds, screen_name, num_notices, is_suspended, time]
            notice_rows.append(",".join([str(cell) for cell in row]))
    with open(output_path, 'a') as f:
        f.write("\n" + "\n".join(notice_rows))
    #with open(output_max_path, 'a') as f:
    #    f.write("\n" + datetime.datetime.utcfromtimestamp(notice_rows[-1]))


#######################

# fixing bug in above script where i lost all the suspended accounts :(
# from (already generated) retrieved_tweets, create new twitter_notices_accounts_tweet_times_


output_path = "twitter_notices_accounts_tweet_times_080116-112116_v2.csv"
labels = ["notice_id", "notice_timestamp", "screen_name", "num_notices", "is_suspended", "tweet_timestamp"]
with open(output_path, 'w') as f:
    f.write(",".join(labels))

epoch = datetime.datetime.utcfromtimestamp(0)
#retrieved_tweets = {}   # retrieved_tweets[screen_name] = []
retrieved_tweets_v2 = {}
duplicate_accounts = 0
for id in notices.keys():
    notice_rows = []
    notice_datetime_timestamp = datetime.datetime.strptime(notices[id]["timestamp"], "%Y-%m-%dT%H:%M:%SZ") # 2016-11-27T23:51:56Z
    notice_seconds = (notice_datetime_timestamp - epoch).total_seconds()
    for screen_name in notices[id]["screen_names"]:
        is_suspended = False
        num_notices = len(screen_names_to_notice_timestamps[screen_name])
        if screen_name in retrieved_tweets_v2:
            duplicate_accounts += 1
            #print("duplicate screen name: {0} !!!".format(screen_name))
        else:
            retrieved_tweets_v2[screen_name] = []
            if screen_name in retrieved_tweets:
                retrieved_tweets_v2[screen_name] = retrieved_tweets[screen_name][:]
            else:
                print("retrieving tweets for {0}".format(screen_name))
                retrieved_tweets_v2[screen_name] = get_tweet_times(screen_name)
            if (retrieved_tweets_v2[screen_name]) == ["SUSPENDED!"]:
                is_suspended = True
                row = [id, notice_seconds, screen_name, num_notices, is_suspended, ""]
                notice_rows.append(",".join([str(cell) for cell in row]))                
            else:
                for time in retrieved_tweets_v2[screen_name]:
                    row = [id, notice_seconds, screen_name, num_notices, is_suspended, time]
                    notice_rows.append(",".join([str(cell) for cell in row]))
    with open(output_path, 'a') as f:
        f.write("\n" + "\n".join(notice_rows))
    #with open(output_max_path, 'a') as f:
    #    f.write("\n" + datetime.datetime.utcfromtimestamp(notice_rows[-1]))

print("duplicate_accounts: {0}".format(duplicate_accounts))

########################
###########################

path = "twitter_notices_accounts_tweet_times_080116-112116.csv"
path_v2 = "twitter_notices_accounts_tweet_times_080116-112116_v2.csv"
output_path = "twitter_notices_accounts_tweets_per_day_080116-112116_pruned.csv"


tweets = {} # tweets[screen_name] = {notice_id:, notice_timestamp: , is_suspended: , times: [tweet_time  -notice_time]}
tweets_multiple_notices = {}
with open(path_v2, 'r') as f:
    lines = f.readlines()
for i in range(1, len(lines)):
    line = lines[i]
    cells = line.split(",")
    if len(cells) == 6:
        cells[-1] = cells[-1].replace("\n","")
        notice_id = cells[0]
        notice_timestamp = cells[1]
        screen_name = cells[2]    
        num_notices = int(cells[3])
        is_suspended = cells[4]
        timestamp = cells[5]
        try:
            timestamp = float(timestamp)
        except:
            if is_suspended == "False":
                datetime_timestamp = datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
                timestamp = (datetime_timestamp - epoch).total_seconds()
        if screen_name not in tweets:
            account_tweets = {
                "notice_id": notice_id, 
                "notice_timestamp": notice_timestamp, 
                "is_suspended": is_suspended, 
                "num_notices": num_notices,
                "times": []}
        if is_suspended == "False":
            account_tweets["times"].append(int(float(timestamp) - float(notice_timestamp)))
        if num_notices == 1:
            # remove accounts that received more than 1 notice
            tweets[screen_name] = account_tweets
        else:
            tweets_multiple_notices[screen_name] = account_tweets
    else:
        # empty line
        pass

############

# count number of suspended accounts

num_accounts_with_one_notice = len(tweets)
num_accounts_with_multiple_notices = len(tweets_multiple_notices)

num_alive_accounts_with_one_notice = len([screen_name for screen_name in tweets if tweets[screen_name]["is_suspended"] == "False"])
num_alive_accounts_with_multiple_notices = len([screen_name for screen_name in tweets_multiple_notices if tweets_multiple_notices[screen_name]["is_suspended"]  == "False"])

ratio_alive_one_notice = float(num_alive_accounts_with_one_notice)/num_accounts_with_one_notice
ratio_alive_multiple_notice = float(num_alive_accounts_with_multiple_notices)/num_accounts_with_multiple_notices

print(num_accounts_with_one_notice)
print(num_accounts_with_multiple_notices)
print(num_alive_accounts_with_one_notice)
print(num_alive_accounts_with_multiple_notices)
print(ratio_alive_one_notice)
print(ratio_alive_multiple_notice)

"""

>>> print(num_accounts_with_one_notice)
19785
>>> print(num_accounts_with_multiple_notices)
12106

>>> print(num_alive_accounts_with_one_notice)
1084
>>> print(num_alive_accounts_with_multiple_notices)
532

>>> print(ratio_alive_one_notice)
0.0547889815517
>>> print(ratio_alive_multiple_notice)
0.0439451511647

"""

##############


tweets_per_day = {}
tweets_per_day_multiple_notices = {}
for (tweets_obj, tweets_per_day_obj) in [(tweets, tweets_per_day), (tweets_multiple_notices, tweets_per_day_multiple_notices)]:
    total_accounts = 0
    enough_data_accounts = 0
    suspended_accounts = 0
    enough_and_not_suspended = 0
    for screen_name in tweets_obj:
        total_accounts += 1
        tweet_days = [int(tweet/60/60/24) for tweet in tweets_obj[screen_name]["times"]]
        set_days = set(tweet_days)
        min_day = min(set_days) if len(set_days) > 0 else 0
        max_day = max(set_days) if len(set_days) > 0 else 0
        suspended_accounts += 1 if tweets_obj[screen_name]["is_suspended"] == "True" else 0
        if min_day < -14 and max_day > 14:  # remove accounts that don't have enough data in surrounding month
            enough_data_accounts += 1
            enough_and_not_suspended += 1 if tweets_obj[screen_name]["is_suspended"] == "False" else 0
            tweets_per_day_obj[screen_name] = {
                "notice_id": tweets_obj[screen_name]["notice_id"], 
                "notice_timestamp": tweets_obj[screen_name]["notice_timestamp"], 
                "is_suspended": tweets_obj[screen_name]["is_suspended"],
                "num_notices": tweets_obj[screen_name]["num_notices"], 
                "times": []}
            tweets_per_day_obj[screen_name]["times"] = [
                (x,tweet_days.count(x)) if x in tweet_days else (x,0) for x in range(min(set_days), max(set_days)+1)]
        else:
            #print("num notices: {0}, num tweets: {1}".format(tweets_obj[screen_name]["num_notices"], len(tweet_days)))
            #not_enough_data_accounts += 1
            pass
    print("total_accounts: {0}".format(total_accounts))
    print("enough_data_accounts: {0}".format(enough_data_accounts))
    print("suspended_accounts: {0}".format(suspended_accounts))
    print("enough_and_not_suspended: {0}".format(enough_and_not_suspended))

"""

one_notice:
    total_accounts: 19785
    enough_data_accounts: 740
    suspended_accounts: 18701
    enough_and_not_suspended: 740

    >>> 19785-18701
    1084 not suspended accounts

    enough_and_suspended = 0, obviously

multiple notices:
    total_accounts: 12106
    enough_data_accounts: 0
    suspended_accounts: 11574
    enough_and_not_suspended: 0

so we don't look at tweets_per_day_multiple_notices


"""

#len(tweets_per_day) = 740
#len(tweets_per_day_multiple_notices) 0

output_path = "twitter_notices_accounts_tweets_per_day_080116-112116_pruned.csv"
labels = ["notice_id", "notice_timestamp", "screen_name", "num_notices", "is_suspended", "total_tweets", "day_num", "tweets_per_day"]
rows = [",".join(labels)]
for screen_name in tweets_per_day:
    notice_id = tweets_per_day[screen_name]["notice_id"]
    notice_timestamp = tweets_per_day[screen_name]["notice_timestamp"]
    num_notices = tweets_per_day[screen_name]["num_notices"]
    is_suspended = tweets_per_day[screen_name]["is_suspended"]
    total_num_notices = sum([num_tweets for (day_num, num_tweets) in tweets_per_day[screen_name]["times"]])
    for (day_num, num_tweets) in tweets_per_day[screen_name]["times"]:
        row = [notice_id, notice_timestamp, screen_name, num_notices, is_suspended, total_num_notices, day_num, num_tweets]
        rows.append(",".join([str(x) for x in row]))
with open(output_path,"w") as f:
    f.write("\n".join(rows))

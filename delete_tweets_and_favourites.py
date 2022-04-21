import requests
import os
from requests.structures import CaseInsensitiveDict
import json
import matplotlib.pyplot as plt
import time

def connect_to_endpoint(url, userid, cursor=None):
    params = {
        'variables': '{"userId":"' + userid + '","count":40,"includePromotedContent":true,"withCommunity":true,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":true,"__fs_responsive_web_like_by_author_enabled":false,"__fs_dont_mention_me_view_api_enabled":true,"__fs_interactive_text_enabled":true,"__fs_responsive_web_uc_gql_enabled":false,"__fs_responsive_web_edit_tweet_api_enabled":false}',
    }
    if cursor:
        params = {
            'variables': '{"userId":"' + userid + '","count":40,"cursor":"' + cursor + '","includePromotedContent":true,"withCommunity":true,"withSuperFollowsUserFields":true,"withDownvotePerspective":false,"withReactionsMetadata":false,"withReactionsPerspective":false,"withSuperFollowsTweetFields":true,"withVoice":true,"withV2Timeline":true,"__fs_responsive_web_like_by_author_enabled":false,"__fs_dont_mention_me_view_api_enabled":true,"__fs_interactive_text_enabled":true,"__fs_responsive_web_uc_gql_enabled":false,"__fs_responsive_web_edit_tweet_api_enabled":false}',
        }

    response = requests.get(url, headers=headers, params=params, cookies=cookies)
    return response.json()

def process_tweets_response(json_response, userId, likeTweets):
    instructions = json_response["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
    data = None
    stop = False
    cursor = None
    ids = set()

    for i in instructions:
        if i["type"] == "TimelineAddEntries":
            data = i["entries"]
        if i["type"] == "TimelineTerminateTimeline" and i["direction"] == "Bottom":
            stop = True
    
    if data == None:
        return ([], cursor, True)

    for item in data:
        try: 
            if item["entryId"].startswith("homeConversation"):
                conversation_items = item["content"]["items"]

                for conversation in conversation_items:
                    id = conversation["item"]["itemContent"]["tweet_results"]["result"]["rest_id"]
                    ids.add(id)
            
            elif item["entryId"].startswith("tweet"):
                result = item["content"]["itemContent"]["tweet_results"]["result"]
                id = result["rest_id"]
                if likeTweets:
                    ids.add(id)
                elif result["legacy"]["user_id_str"] == str(userId): #check to make sure the tweet in the thread belongs to the user
                    ids.add(id)
            
            elif item["entryId"].startswith("cursor-bottom"):
                cursor = item["content"]["value"]
        except:
            continue

    return (list(ids), cursor, stop)

def get_tweets(tweets_url, userid, cursor=None, likeTweets=False):
    tweet_ids = set()
    stop = False
    
    while not stop:
        json_response = connect_to_endpoint(tweets_url, userid, cursor)
        ids, cursor, stop = process_tweets_response(json_response, userid, likeTweets)
        len_old = len(tweet_ids)
        tweet_ids.update(ids)
        len_new = len(tweet_ids)
        if len_old == len_new:
            break

        print("⬇ Downloaded", len(ids), "tweets. Total unique tweets fetched: ", len(tweet_ids))

    print("Total: ", len(tweet_ids), " tweets found in this iteration. 🐤")

    return list(tweet_ids)

def delete_tweet(url, tweet_id, text):
    json_data = {
        'variables': '{"tweet_id":"'+ tweet_id + '","dark_request":false}',
        'queryId': 'VaenaVgh5q5ih7kvyVjgtg',
    }
    response = requests.post(url, headers=headers, cookies=cookies, json=json_data)

    if response.status_code == 200:
        print(text, tweet_id)
    else:
        print("❌ Oops something went wrong. Don't worry lets keep going.")

def delete_tweets(url, ids):
    print("🚮 Deleting", len(ids), "tweets.")

    for id in ids:
        delete_tweet(url, id, "✅ Deleted: ")
        time.sleep(2) #Make the program sleep for 2 seconds to make sure we not reach the twitter api limit

def unfavourite_tweets(url, ids):
    print("👎🏼 Unfavouriting", len(ids), "tweets.")

    for id in ids:
        delete_tweet(url, id, "💔 Un-favourite: ")
        time.sleep(2) #Make the program sleep for 2 seconds to make sure we not reach the twitter api limit

cookies = {
    'guest_id_marketing': 'v1%3A164669839006955000',
    'guest_id_ads': 'v1%3A164669839006955000',
    'kdt': 'bJhJox5mrrrW9YL31dig3hjZzwtYxMNtt3gWz9Kh',
    'dnt': '1',
    'lang': 'en',
    'at_check': 'true',
    'des_opt_in': 'Y',
    'csrf_id': 'fff51a1b4845c2e71bd6536456db5a34',
    'att': '1-vnkTZ2r9hJhYpqM8H0COVBmskIFXg8NqKdqFcbkU',
    '_sl': '1',
    'personalization_id': '"v1_+Ne/LiItHdp0/OBMp52W1A=="',
    'guest_id': 'v1%3A165057133129728834',
    'gt': '1517232249644617728',
    'auth_token': '3ca0a47281df2185e7jsbfjdh60f7fb7bc068c',
    'ct0': 'f22f1f6bb7d28686f7efdb86fb2291a811952d0dd277c2aee99f03f4d22a784fd6794c0915cf096eab2318805016d0e92afc00008260973afdf53539ec6f968715c4f5f14f4d187066139bbe3feff638',
    'twid': 'u%3D1517233098756292608',
    '_twitter_sess': 'BAh7CCIKZmxhc2hJQzonQWN0aW9uQ29udHJvbGxlcjo6Rmxhc2g6OkZsYXNo%250ASGFzaHsABjoKQHVzZWR7ADofbGFzdF9wYXNzd29yZF9jb25maXJtYXRpb24i%250AFTE2NTA1NzE1NzM3NDcwMDA6HnBhc3N3b3JkX2NvbmZpcm1hdGlvbl91aWQi%250AGDE1MTcyMzMwOTg3NTYyOTI2MDg%253D--d099f5e2cd39af981d53f46629d19394702c239f',
    'mbox': 'PC#5a3221c3daf94883a14095c1b9f300e7.34_0#1713816525|session#45917ba21b024a1d8dcfe9624aca01a8#1650573585',
    'external_referer': 'padhuUp37ziAYt49cfJv%2FPYan957PLwSgO%2FWRGmTwuk%3D|0|8e8t2xd8A2w%3D',
}

headers = {
    'authority': 'twitter.com',
    'accept': '*/*',
    'accept-language': 'en-US,en;q=0.9',
    'authorization': 'Bearer AAAAAAAAAAAAAAAAAAAAANRILgkdfhghjfdsbkjdsfgq16cHjhLTvJu4FA33AGWWjCpTnA',
    'cache-control': 'no-cache',
    'origin': 'https://twitter.com',
    'pragma': 'no-cache',
    'referer': 'https://twitter.com/jadacryptoguy/with_replies',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36',
    'x-csrf-token': 'f22f1f6bbksfgdhjbf99f03f4d22a784fd6794c0915cf096eab2318805016d0e92afc00008260973afdf53539ec6f968715c4f5f14f4d187066139bbe3feff638',
    'x-twitter-active-user': 'yes',
    'x-twitter-auth-type': 'OAuth2Session',
    'x-twitter-client-language': 'en',
}

def main():
    userid = "1234"
    tweets_url = 'https://twitter.com/i/api/graphql/sakfdhbfajdsblj/UserTweetsAndReplies'
    delete_url = 'https://twitter.com/i/api/graphql/jkadbfsiudbfakjsldzf/DeleteTweet'
    likes_url = 'https://twitter.com/i/api/graphql/asdfjksdjnfkdsljb/Likes'
    unfavourite_url = 'https://twitter.com/i/api/graphql/flshfjksjdbfj/UnfavoriteTweet'

    print("🧹 Starting Twitter cleanup. Go make yourself a cup of coffee 🧋. This will take some time. 😴")
    
    complete = False
    while not complete:
        ids = get_tweets(tweets_url, userid)
        delete_tweets(delete_url, ids)
        if len(ids) == 0:
            complete = True

    print("Hurrah!!💃🏻 All tweets deleted.")
    print("🧹 Starting to unfavourite tweet.")

    complete = False
    while not complete:
        ids = get_tweets(likes_url, userid, None, True)
        unfavourite_tweets(unfavourite_url, ids)
        if len(ids) == 0:
            complete = True

    print("Hurrah!!💃🏻 Cleanup complete.")

if __name__ == "__main__":
    main()

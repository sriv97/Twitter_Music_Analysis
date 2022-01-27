import requests
import os
import json
import config
import re

bearer_token = config.BEARER_TOKEN

search_url = "https://api.twitter.com/2/tweets/search/recent"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': 'justin bieber music','tweet.fields': 'author_id'}

def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()

def main():
    json_response = connect_to_endpoint(search_url, query_params)
    for x in range(len(json_response['data'])):
        author_id = json_response['data'][x]['author_id']
        tweet_id = json_response['data'][x]['id']
        text = json_response['data'][x]['text']
        str_en = text.encode("ascii", "ignore")
        str_de = str_en.decode()
        retweet_check = re.match("RT +@[^ :]+:?", str_de)
        match = re.findall("(?<=\:)(.*)", str_de)
        text_raw = match[0]
        text = " ".join(text_raw.split())
        retweet=bool(retweet_check)
        print('Author ID: ',author_id)
        print('Tweet ID: ',tweet_id)
        print('Is Retweet: ', retweet)
        print('Final Text: ', text)
        #if retweet is True:
    print(json_response['meta']['next_token'])
    #print(json.dumps(json_response, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()

import requests
import os
import json
import config #local file which contains all the secret keys
import re
import mysql.connector

bearer_token = config.BEARER_TOKEN

search_url = "https://api.twitter.com/2/tweets/search/recent"

# Optional params: start_time,end_time,since_id,until_id,max_results,next_token,
# expansions,tweet.fields,media.fields,poll.fields,place.fields,user.fields
query_params = {'query': 'justin bieber music','tweet.fields': 'author_id,created_at,text','max_results':10}

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

def db_connect():
    mydb = mysql.connector.connect(
    host="localhost",
    user="sri",
    password="Twittermusic1!",
    database="twitter_music"
    )
    return mydb

def get_historical_tweets():
        json_response = connect_to_endpoint(search_url, query_params)
        data_list = []
        for x in range(len(json_response['data'])):
            data = {}
            data['author_id'] = json_response['data'][x]['author_id']
            data['tweet_id'] = json_response['data'][x]['id']
            text = json_response['data'][x]['text']
            str_en = text.encode("ascii", "ignore")
            str_de = str_en.decode()
            retweet_check = re.match("RT +@[^ :]+:?", str_de)
            if retweet_check:
                match = re.findall("(?<=\:)(.*)", str_de)
                text_raw = match[0]
                data['text'] = " ".join(text_raw.split())
            else:
                data['text'] = str_de
            data['retweet']=bool(retweet_check)
            date_time = re.findall("[^Z]*",json_response['data'][x]['created_at'])
            data['created_at']= date_time[0]
            print(json.dumps(data, indent=4, sort_keys = True))
            data_list.append(data)
        save_to_db('justin_bieber',data_list)    

def save_to_db (table_name, data_list):
    db_cnx = db_connect()
    db_cur = db_cnx.cursor()
    column_names = ", ".join(data_list[0].keys())
    column_values = '%(' + ')s, %('.join(data_list[0].keys())+')s'
    db_cur.executemany (f'INSERT INTO {table_name} ({column_names}) values ({column_values})', data_list)
    db_cnx.commit()
    
def main():
    get_historical_tweets()
    #print(json_response['meta']['next_token'])
   # db_cnx.close()
    #print(json.dumps(json_response, indent=4, sort_keys=True))

if __name__ == "__main__":
    main()

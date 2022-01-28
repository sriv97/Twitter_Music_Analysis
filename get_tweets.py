import requests
import os
import json
import config #local file which contains all the secret keys
import re
import mysql.connector
from time import sleep


bearer_token = config.BEARER_TOKEN

search_url = "https://api.twitter.com/2/tweets/search/recent"

#default query params to get first pagination of data
query_params = {'query': 'justin bieber music','tweet.fields': 'author_id,created_at,text','max_results':50}

#query params payload for a recursive call
query_params_recursive = {
    "query": "justin bieber music",
    "tweet.fields": "author_id,created_at,text",
    "max_results": 10,
    "next_token": None,
}


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer {bearer_token}"
    r.headers["User-Agent"] = "v2RecentSearchPython"
    return r

#Calling Twitter Endpoint
def connect_to_endpoint(url, params):
    response = requests.get(url, auth=bearer_oauth, params=params)
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(response.status_code, response.text)
    return response.json()


#Credentials for local mysql DB 
def db_connect():
    mydb = mysql.connector.connect(
    host="localhost",
    user="sri",
    password="Twittermusic1!",
    database="twitter_music"
    )
    return mydb

data_list = []

#saving records in the database
def save_to_db (table_name, data_list):
    db_cnx = db_connect()
    db_cur = db_cnx.cursor()
    column_names = ", ".join(data_list[0].keys())
    column_values = '%(' + ')s, %('.join(data_list[0].keys())+')s'
    db_cur.executemany (f'INSERT INTO {table_name} ({column_names}) values ({column_values})', data_list)
    db_cnx.commit()

def get_initial_tweets():
    json_response = connect_to_endpoint(search_url, query_params)
    create_dictionary(json_response) 

def get_recursive_tweets(token):
    query_params_recursive['next_token']=token
    if len(data_list) == 300:
        f = open("next_token.txt", "w")
        f.write(str(token))
        f.close()
        save_to_db('justin_bieber',data_list)
    else:
        json_response = connect_to_endpoint(search_url, query_params)
        create_dictionary(json_response)

def create_dictionary(json_response):
    for x in range(len(json_response['data'])):
        data = {} #creating empty dictionary
        data['author_id'] = json_response['data'][x]['author_id'] #assigning value to author_id
        data['tweet_id'] = json_response['data'][x]['id'] #assigning value to tweet_id
        text = json_response['data'][x]['text'] 
        str_en = text.encode("ascii", "ignore") #decoding text values
        str_de = str_en.decode()
        retweet_check = re.match("RT +@[^ :]+:?", str_de) #checking if the tweet is a retweet based on regex
        if retweet_check: #if it is a regex, then skip to the main part of the tweet
            match = re.findall("(?<=\:)(.*)", str_de)
            text_raw = match[0]
            data['text'] = " ".join(text_raw.split())
        else:
            data['text'] = str_de
            data['retweet']=bool(retweet_check) #assigning a boolean value for retweet
            date_time = re.findall("[^Z]*",json_response['data'][x]['created_at']) #removing the last char in the default API timestamp
            data['created_at']= date_time[0]
            #print(json.dumps(data, indent=4, sort_keys = True))
        data_list.append(data) # adding individual record to the array        
    token = json_response['meta']['next_token'] #capturing the next_token value
    if token:
            get_recursive_tweets(token) #if a token exists call the recursive function
    else: #if we completed all the remaining tweets, we can delete the file
        file_exists = os.path.exists('next_token.txt')
        if file_exists:
            os.remove("next_token.txt")

def main():
    file_exists = os.path.exists('next_token.txt') #check if file already exists
    if file_exists: #if the file exists read token from there
        with open('next_token.txt') as g:
            token = g.read()
            get_recursive_tweets(token)
    else:
        get_initial_tweets() #assume its a fresh start

if __name__ == "__main__":
    main()
import mysql.connector

mydb = mysql.connector.connect(
  host="localhost",
  user="sri",
  password="Twittermusic1!",
  database="twitter_music"
)

mycursor = mydb.cursor()

mycursor.execute("CREATE DATABASE IF NOT EXISTS twitter_music")

mycursor.execute("CREATE TABLE IF NOT EXISTS justin_bieber (author_id BIGINT, \
    tweet_id BIGINT, \
    text VARCHAR(280) NOT NULL, \
    retweet BOOLEAN, \
    created_at DATETIME \
    )")

mydb.close()
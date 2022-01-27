/*
Top Users who retweet
*/
Select
   author_id,
   sum(case when retweet = TRUE then 1 else 0 end) 
from
   justin_bieber 
group by
   author_id
order by
    2 desc

/*
Top Tweets that are retweeted
*/
Select
    tweet,
    count(1)
from
    justin_bieber
group by
    tweet
order by
    2 desc

/*
Count of unique tweets
*/
Select
    count(1)
from
    justin_bieber
where
    retweet = FALSE

def handler(event, context):
    import tweepy
    import json
    import boto3

    # Create a Secrets Manager client
    session = boto3.session.Session()
    client = session.client(
        service_name='secretsmanager',
        region_name=event['region_name']
    )

    get_secret_value_response = client.get_secret_value(SecretId=event['secret_name'])
    secret = get_secret_value_response['SecretString']
    secret = json.loads(secret)
    consumer_key = secret['APIKey']
    consumer_secret = secret['APIKeySecret']
    access_token = secret['AccessToken']
    access_secret = secret['AccessTokenSecret']

    class MyStreamListener(tweepy.Stream):

        def on_data(self, data):
            tweet = json.loads(data)
            if tweet:
                try:
                    if not tweet['text'].startswith('RT'):
                        response = {'created_at': tweet['user']['created_at'],
                                    'handle': tweet['user']['screen_name'],
                                    'text': tweet['text'],
                                    'favourite_count': tweet['user']['favourites_count'],
                                    'retweet_count': tweet['retweet_count'],
                                    "retweeted": tweet['retweeted'],
                                    'followers_count': tweet['user']['followers_count'],
                                    'friends_count': tweet['user']['friends_count'],
                                    'location': tweet['user']['location'],
                                    'lang': tweet['user']['lang']
                                    }
                        print(f"{response} \n")
                except KeyError: # getting empty json in between stream so ignore these
                    pass

    if event['delivery'] == "stream":
        stream = MyStreamListener(consumer_key, consumer_secret, access_token, access_secret)
        stream.filter(track=event.get('keyword'))
    elif event['delivery'] == 'search':

        auth = tweepy.OAuth1UserHandler(
            consumer_key, consumer_secret, access_token, access_secret
        )

        api = tweepy.API(auth,  wait_on_rate_limit=True)
        for tweet in tweepy.Cursor(api.search_tweets, event.get('keyword'), count=100).items():
            if not tweet.text.startswith('RT'):
                response = {'created_at': tweet.created_at,
                            'handle': tweet.user.screen_name,
                             'text': tweet.text,
                             'favourite_count':tweet.user.favourites_count,
                             'retweet_count': tweet.retweet_count,
                            "retweeted": tweet.retweeted,
                             'followers_count': tweet.user.followers_count,
                             'friends_count':tweet.user.friends_count,
                             'location': tweet.user.location,
                             'lang': tweet.user.lang
                             }
                print(response)

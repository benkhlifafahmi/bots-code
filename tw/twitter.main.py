
import time
from Twitter import TwitterClient
from dotenv import dotenv_values

def main():
    config = dotenv_values('.env')
    username = config['TW_LOGIN']
    password = config['TW_PASSWORD']
    client = TwitterClient('./session_chrome/')
    """
    #login to twitter
    client.login(username=username, password=password)
    
    #get logged in status
    log_status = client.is_logged_in()
    print('[+] Logged in status is : ', log_status)

    #get current trends with element on it
    trends = client.get_trends()
    print(trends)
    tweets = client.walk_home()
    for tweet in tweets:
        print(tweet)
    last_tweet = tweets[-1]
    print('---------------------------------')
    print('[+] Getting more data from the feed')
    tweets = client.get_more_tweets(previously_scrapped=len(tweets), tweets_count=5, last_element=last_tweet)
    for tweet in tweets:
        print(tweet)
    """
    client.close()
if __name__ == '__main__':
    main()
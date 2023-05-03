
import time
from Youtube import YoutubeClient
from dotenv import dotenv_values

def main():
    config = dotenv_values('../.env')
    username = config['GG_LOGIN']
    password = config['GG_PASSWORD']
    client = YoutubeClient()#'./session_chrome/')
    """
    #login to the client youtube
    logged_in = client.is_logged_in()
    if not logged_in:
        client.login(username, password)
    else:
        print('[!] skip loging in')

    #testing habit to watch video and skip ads during the watch
    total_seconds = client.watch_video('YG_x_AS6PCU')
    #search youtube for term and get specific results
    result = client.search_youtube('ricky martin')
    print(result)
    location = result[-1]['cord']['location']
    new_result = client.get_more_results(location)
    print(new_result)    
    result = client.search_youtube('ricky martin')
    video = result[1]

    #Toggle Like
    client.watch_video(video_element=video['web_element'])
    """
    client.like_video(video_id='YG_x_AS6PCU')
    client.watch_video(video_id='yHJ2Al0Qd-w')
    """
    time.sleep(3)
    client.like_video()
    time.sleep(4)
    client.like_video(remove_like=True)


    #subscription process
    client.open_video(video_id='XRoBSJ2kk2I')
    print(client.is_subscribed(video_id='XRoBSJ2kk2I'))
    time.sleep(2)
    client.subscribe_channel(video_id='XRoBSJ2kk2I')
    time.sleep(3)
    print(client.is_subscribed(video_id='XRoBSJ2kk2I'))
    time.sleep(2)
    client.unsubscribe_channel(video_id='XRoBSJ2kk2I')
    time.sleep(4)
    print(client.is_subscribed(video_id='XRoBSJ2kk2I'))
    """
    client.close()
if __name__ == '__main__':
    main()
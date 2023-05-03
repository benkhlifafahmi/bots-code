
import time
from Facebook import FacebookClient
from dotenv import dotenv_values

def main():
    config = dotenv_values('.env')
    username = config['FB_LOGIN']
    password = config['FB_PASSWORD']
    client = FacebookClient('./session_chrome/')
    #client.login(username, password)
    #result = client.write_post_to_feed('شن علاج الصقع في الليل')
    #if result:
    #    print("[+] Posted successfully to your wall")
    #else:
    #    print("[-] There was an error posting to your facebook account")
    posts_list = client.extract_posts_in_group('1106364519835217')
    print(posts_list)
    #client.leave_group('811380449549677')
    #can_post = client.can_post_to_group('GamesMix')
    #print('has the ability to post ? ', can_post)
    #client.write_post_to_group(group_id='1563253290392558', content='The best song ever <3 https://www.youtube.com/watch?v=ZjDZrReZ4EI')
    #client.group_commet_post(group_id='1563253290392558', post_id='4750543464996842', content='Nice one <3')
    #client.group_react_post(group_id='1563253290392558', post_id='4756721181045737', reaction='Sad')
    time.sleep(5)
    client.close()
if __name__ == '__main__':
    main()
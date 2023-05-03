
import time
from Facebook import Facebook
from dotenv import dotenv_values

def main():
    config = dotenv_values('.env')
    username = config['FB_LOGIN'] #extract username from the ENV
    password = config['FB_PASSWORD'] #extract the password from the ENV
    client = Facebook(
        browser="Chrome",  #create Chrome 
        session_path="chrome_session", # save the session into a folder chrome_session
        version=97, # version 97 of chrome (change it to yours own version)
        headless=None #run in GUI.
    )
    """
    #--------- TEST 1 ---------
    #!  Check authentication  !
    print('-------------- F1: IS AUTHENTICATED ------------------')
    is_authenticated = client.is_authenticated() #check the status
    print(f"this session status is : {is_authenticated}") #print the status

    """
    #--------- TEST 2 ---------
    #!     Authentication     !
    print('-------------- F2: AUTHENTICATION ------------------')
    authentication_result = client.login(username=username, password=password)
    print(f"this authentication result was : {authentication_result}") #print the status
    """
    #--------- TEST 3 ---------
    #!    Write Post to FB    !
    print('-------------- F3: POST TEXT TO FB ------------------')
    create_post_result = client.write_post(content="Hey Everyone")
    print(f"The result was : {create_post_result}") #print the status
    
    #--------- TEST 4.1 ---------
    #!        Join Group        !
    print('-------------- F4.1: JOIN GROUP ------------------')
    group_join_result = client.join_group(group_id="1955658991244886")
    print(f"The result was : {group_join_result}") #print the status
    
    time.sleep(4)
    #--------- TEST 4.2 ---------
    #!    Check Membership Status   !
    print('-------------- F4.2: CHECK MEMBERSHIP ------------------')
    membership_code = client.is_member_of_group(group_id="1955658991244886")
    print(f"The result was : {membership_code}") #print the status
    
    #--------- TEST 4.3 ---------
    #!    Leave group result    !
    print('-------------- F4.3: LEAVE GROUP ------------------')
    leave_group_result = client.leave_group(group_id="1955658991244886")
    print(f"The result was : {leave_group_result}") #print the status
    
    #------------ TEST 5 ------------
    #!    Post to specific gorup    !
    print('-------------- F5: WRITE POST TO GROUP ------------------')
    did_post = client.write_post_to_group(group_id="1955658991244886", content="Hey Everyone")
    print(f"The result was : {did_post}") #print the status
    

    #------------ TEST 6.1 ------------
    #!    React to specific post in gorup    !
    print('-------------- F6.1: REACT TO POST IN GROUP ------------------')
    did_react = client.group_react_post(group_id="1955658991244886", post_id="2593509520793160", reaction="Care")
    print(f"The result was : {did_react}") #print the status
    time.sleep(2)
    #------------ TEST 6.2 ------------
    #!    React to specific post in gorup    !
    print('-------------- F6.2: REMOVE REACT FROM POST IN GROUP ------------------')
    did_remove_react = client.group_remove_interaction_with_post(group_id="1955658991244886", post_id="2593509520793160")
    print(f"The result was : {did_remove_react}") #print the status
    
    #------------ TEST 7 ------------
    #!    Extract specific number of posts from group    !
    print('-------------- F7: SCROLL IN GROUP ------------------')
    posts = client.scroll_group(group_id="1955658991244886", num_of_post=100)
    print(f"The result was : {len(posts)}/100 posts") #print the status
    
    #------------ TEST 8 ------------
    #!    Extract specific number of posts from group    !
    print('-------------- F8: Like Page ------------------')
    liked = client.like_page(page_uname="m99.dandana")
    print(f"The result was : {liked}") #print the status

    #------------ TEST 9 ------------
    #!    Extract specific number of posts from page    !
    print('-------------- F9: SCROLL IN PAGE ------------------')
    posts = client.scroll_page(page_uname="m99.dandana", num_of_post=100)
    print(f"The result was : {len(posts)}/100 posts") #print the status
    
    print('-------------- F9.1: GET POST TYPE ------------------')
    for post in posts:
        print('Visible post now is : ', client.what_kind(el=post['element']))
        input()
    posts = client.scroll_page(page_uname="m99.dandana", num_of_post=3)
    post = posts[0]
    #toggle the play button (play video)
    client.toggle_play(el=post['element'])
    time.sleep(3) #wait 3 seconds and 
    current_time = client.current_time(el=post['element'])
    total_time = client.total_time(el=post['element'])
    print(f'current time is {current_time}/{total_time}')
    #pause the video
    client.toggle_play(el=post['element'])
    """


    time.sleep(10) #keep the browser 10 sec if u need to check smthg


if __name__ == '__main__':
    main()
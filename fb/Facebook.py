import time
from tokenize import group
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

#FACEBOOK GROUP MEMBERSHIP STATUS
ALREADY_MEMBER = 1
PENDING_MEMBER = 0
NOT_MEMBER = -1
ERR = -99
#FACEBOOK REACTION
LOVE_REACTION = "Love"
LIKE_REACTION = "Like"
CARE_REACTION = "Care"
SAD_REACTION = "Sad"
ANGRY_REACTION = "Angry"
WOW_REACTION = "Wow"
HAHA_REACTION = "Haha"
#FACEBOOK GET POST TYPE
ERR_GET_TYPE = "ERR_GET_TYPE"
VIDEO_POST = "VIDEO_POST"
PICTURE_POST = "PICTURE_POST"
TEXT_POST = "TEXT_POST"
TEXT_BG_POST = "TEXT_BG_POST"


class Facebook:
    

    def __init__(self, browser="chrome", session_path=None, headless=None, version=97):
        self.driver = None
        if browser.lower() == "chrome":
            import undetected_chromedriver.v2 as UC #import undetected chrome 
            #setup browser option
            options = UC.ChromeOptions() 
            #disable the GPU
            options.add_argument("--disable-gpu") 
            options.add_argument("--disable-dev-shm-usage")
            #disable notification to avoid non-clickable webelement issue
            options.add_argument("--disable-notifications") 
            
            if session_path is not None:
                #store the user session to the specified path
                options.add_argument('--user-data-dir='+session_path)
            
            if headless is not None:
                #run the browser in the headless mode.
                options.add_argument('--headless')
            #set window size to avoid any problem with the responsive websites.
            options.add_argument('--window-size=1920,1080')
            
            #start the chrome browser with the speicifed
            self.driver = UC.Chrome(version=version, options=options)
        elif browser.lower() == "firefox":
            pass
        elif browser.lower() == "safari":
            pass
        elif browser.lower() == "remote":
            pass
    
    def __is_it_facebook(self, url='https://facebook.com', sub_url=''):
        '''
            Private function that check if the current url is facebook
            if not it should redirect either to facebook.com or the url you pass.
        '''
        # check if the current page is facebook.com or not
        if "facebook.com" not in self.driver.current_url:
            #if it's not facebook redirect to the url in the params
            self.driver.get(url)
        # wait for the page to fully load
        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.execute_script('return document.readyState == "complete"')
        )

        # check if the sub_url is not in the current url
        # this might be useful when you want to check if you are already in facebook but yet 
        # you want to verify if the url has a specific parameter.
        if sub_url not in self.driver.current_url:
            self.driver.get(url)
        # wait for the page to load.
        WebDriverWait(self.driver, 30).until(
            lambda driver: driver.execute_script('return document.readyState == "complete"')
        )

    def __extract_n_post(self, num_of_post=10, feed_element=None):
        posts = []
        counter = 1
        try:
            #while we still didn't reach our goal keep going
            while counter <= num_of_post:
                #wait until the next post appear
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((
                    By.XPATH, f'//div[@aria-posinset="{counter}"]'
                )))
                #if the user provide a feed element we scroll inside that feed, other wise we scroll and search in the whole page.
                """
                    this part was created to avoid conflict when you have multiple feed lines (<div role="feed">) in the page like
                    when you have a pinned post in a page, this will create two feed, pinned post will be in feed_1 and the rest in feed_2
                    if you provide the webelement of feed_1 or feed_2 the script will return posts from that feed
                    other wise from both of them.
                """
                if feed_element is not None:
                    #locate the post #{counter} in the feed
                    post = feed_element.find_element(By.XPATH, f'.//div[@aria-posinset="{counter}"]')
                else:
                    #locate the post #{counter} in the feed
                    post = self.driver.find_element_by_xpath(f'//div[@aria-posinset="{counter}"]')
                
                post_height = post.size['height'] + 30

                #scroll to the post element
                actions = ActionChains(self.driver)
                actions.move_to_element(post).perform()
                self.driver.execute_script(f"window.scrollBy(0, {post_height})")
                #add our post to the posts list
                posts.append({
                    'element': post,
                    'location': post.location,
                })
                counter = counter + 1
            return posts
        except Exception as e:
            print(e)
            #return at least what we have collected till we faced an exception
            return posts


    def is_authenticated(self):
        '''
            This function should return boolean (True/False) to 
            indicate if the user is fully authenticated on the platform.
        '''
        self.__is_it_facebook() #if the browser is not on facebook we should just visit facebook
        # check if the authentication email input is visible on the screen 
        try:
            self.driver.find_element_by_xpath('//input[contains(@name, "email")]') #if this did not raise an exception the input is visible
            #we return false because we were able to locate the username input
            return False 
        except NoSuchElementException:
            # if yes then the user is not authenticated other wise the user is authenticated
            return True
        except Exception:
            # TODO - Make the even logger
            # !-- HERE WE CATCH THE REST OF EXCEPTION --! #
            print('[-] Oops!')    
            return False

    def login(self, username=None, password=None):
        '''
            login(username: str, password: str) -> bool:
            perform the authentication on facebook paltform
            and return boolean to describe if the authentication was successful or not.
        '''
        self.__is_it_facebook() #if the browser is not on facebook we should just visit facebook
        if self.is_authenticated(): #check if you are already authenticated
            #already authenticated
            return True
        try:
            #locate the username input (<input name="email" .../>)
            username_input = self.driver.find_element_by_xpath('//input[contains(@name, "email")]')
            #type in the username
            username_input.send_keys(username)
            #locate the password input (<input name="pass" .../>)
            password_input = self.driver.find_element_by_xpath('//input[contains(@name, "pass")]')
            #type in the password
            password_input.send_keys(password)
            #Hit Enter
            password_input.send_keys(Keys.ENTER)
            #wait for page to reload
            WebDriverWait(self.driver, 30).until(
                lambda driver: driver.execute_script('return document.readyState == "complete"')
            )
            # TO verify if the login was done successfully
            return self.is_authenticated() 
        except:
            #TODO - ADD LOGGER
            return False

    def write_post(self, content=None):
        '''
            write_post(content:str) -> bool:
            this function write post to the authenticated user profile
            it take the content to post, and return a boolean flag.

            TODO: 
                - Add media file
                - Set Privacy of the POST
                - Set Background option
                - Add feeling
        '''
        self.__is_it_facebook() #check if we are on facebook ? 
        try:
            actions = ActionChains(self.driver) #create selenium UI action controller.
            actions.send_keys(Keys.HOME).perform(); #scroll to the top of the page.
            #Locate the create post area
            create_post_area = self.driver.find_element_by_xpath('//div[contains(@aria-label, "Create a post")]') #note this works only when you have eng.v
            # TODO!- force english version of facebook or translate the keywoard based on the language
            # Locate the edit text element
            edit_text_element = create_post_area.find_element(By.XPATH, './/div[contains(@role, "button")]')
            edit_text_element.click() #this will open the modal
            WebDriverWait(self.driver, 10).until( # tell selenium to wait (MAX 10 s)
                EC.visibility_of_element_located( # until the visibility of the element
                    (By.XPATH, '//div[contains(@aria-describedby, "placeholder")]')  #located by XPATH (this where the user can type text)
                ))
            #locate the text area
            text_area = self.driver.find_element_by_xpath('//div[contains(@aria-describedby, "placeholder")]')
            text_area.click() #click on it to start typing
            text_area.send_keys(content) #send the content to post
            #locate the button post
            post_btn = self.driver.find_element_by_css_selector('div[aria-label="Post"]')
            post_btn.click() #submit the post
            WebDriverWait(self.driver, 10).until( #wait 10 seconds as max until the button post disapear which mean the modal closed.
                EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Post"]'))
            )
            return True #if we reached this position the post should've been posted successfully.
        except Exception as e:
            #TODO - ADD LOGGER
            return False

    #  ------------  GROUP INTERACTION FUNCS  -------------  #
    def is_member_of_group(self, group_id=None):
        '''
            is_member_of_group(group_id: str) -> int:
            Takes the group_id you want to check, and return True if the current user
            is a member of the group.
            return ALREADY_MEMBER : you are a member
            return PENDING_MEMBER : you are not a member (request pending)
            return NOT_MEMBER : you are not a member
        '''
        self.__is_it_facebook(
            #fallback url if we are not in facebook or if the facebook url is not the group url
            url=f"https://facebook.com/groups/{group_id}", 
            sub_url=f"/groups/{group_id}"
        )
        try:
            try:
                #try to locate the join group button which mean the user is not a member
                self.driver.find_element_by_xpath('//div[contains(@aria-label,"Join group")]')
                return NOT_MEMBER
            except:
                pass

            try:
                #Try to locate the cancel request button to see if the user has a pending request
                self.driver.find_element_by_xpath('//div[contains(@aria-label,"Cancel request")]')
                return PENDING_MEMBER
            except:
                pass
            
            try:
                #if the button joined exist this mean we are already a member of the group.
                self.driver.find_element_by_xpath('//div[contains(@aria-label,"Joined")]')
                return ALREADY_MEMBER
            except:
                pass

            #we should not reach this point, if we do then we have to debug it?
            return ERR
        except:
            #TODO - ADD LOGGER
            return ERR

    def join_group(self, group_id=None):
        '''
            join_group(group_id: str) -> bool:
            Takes the group_id you want to join, and return True if the operation
            was done successfully.
        '''
        self.__is_it_facebook(
            #fallback url if we are not in facebook or if the facebook url is not the group url
            url=f"https://facebook.com/groups/{group_id}", 
            sub_url=f"/groups/{group_id}"
        )

        #check if the user is already a member of the target group
        membership_status = self.is_member_of_group(group_id=group_id)
        if membership_status is not NOT_MEMBER and membership_status is not ERR: # if the current membership is not (NOT_MEMBER) this mean the user has already either a request pending or he is a member already
            return True
        if membership_status is ERR:
            #this mean we have an error checking the group page, require debug for further improvement
            return False 

        try:
            #Locate join group button
            join_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Join group")]')
            join_btn.click()#click join
            #wait until either the status become joined or the cancel request button appear(this case when the group require approval)
            WebDriverWait(self.driver, 10).until(
                lambda driver: driver.find_elements(By.XPATH,'//div[contains(@aria-label,"Joined")]') or driver.find_elements(By.XPATH,'//div[contains(@aria-label,"Cancel request")]')
            )
            return True
        except Exception as e:
            #TODO - ADD LOGGER
            return False

    def leave_group(self, group_id=None):
        '''
            leave_group(group_id: str) -> bool:
            Takes the group_id you want to leave, and return True if the operation
            was done successfully.
        '''
        self.__is_it_facebook(
            #fallback url if we are not in facebook or if the facebook url is not the group url
            url=f"https://facebook.com/groups/{group_id}", 
            sub_url=f"/groups/{group_id}"
        )
        #check if the user is already a member of the target group
        membership_status = self.is_member_of_group(group_id=group_id)
        if membership_status is NOT_MEMBER: # if the user is not a member no need to go further.
            return True #return True.

        if membership_status is ERR:
            #this mean we have an error checking the group page, require debug for further improvement
            return False 

        if membership_status is PENDING_MEMBER:
            try:
                #locate the cancel member request button
                cancel_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Cancel request")]')
                cancel_btn.click() #click the button
                #wait until the button join group appear
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-label,"Join group")]')))
                #return True as the operation was done successfully.
                return True
            except:
                #TODO - ADD LOGGER
                return False
        
        elif membership_status is ALREADY_MEMBER:
            try:
                #locate the joined button
                join_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Joined")]')
                join_btn.click() #click the button
                #wait until the menu list appear
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@role, "menuitem")]')))
                leave_btn = self.driver.find_element_by_xpath('//div[contains(@role,"menuitem")][3]')#select the third menu (which should be leave the group)
                leave_btn.click()
                WebDriverWait(self.driver, 10).until(lambda driver: driver.find_elements(By.XPATH,'//div[contains(@aria-label,"Leave Group")]') or driver.find_elements(By.XPATH,'//div[contains(@aria-label,"Join group")]'))
                try:
                    #locate the confirmation button if there is a popup of confirmation
                    confirm_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Leave Group")]')
                    confirm_btn.click() #click confirm
                except:
                    pass
                #wait until the visbility of the join group button again (max 10s)
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-label,"Join group")]')))
                return True 
            except:
                #TODO - ADD LOGGER
                return False

    def can_post_to_group(self, group_id=None):
        '''
            can_post_to_group(group_id: str) -> bool:
            Takes the group_id you want to post to, and return True if the current user
            has the permission.
        '''
        self.__is_it_facebook(
            #fallback url if we are not in facebook or if the facebook url is not the group url
            url=f"https://facebook.com/groups/{group_id}", 
            sub_url=f"/groups/{group_id}"
        )
        try:
            #try to locate the write new post element in the group home page.
            self.driver.find_element_by_xpath('//div[contains(@data-pagelet,"GroupInlineComposer")]/div/div/div/div[1]/div')
            return True
        except:
            #there was an error locating the new post div, this means the user can't post to the group
            return False
    
    def write_post_to_group(self, group_id=None, content=None):
        '''
            write_post_to_group(group_id: str, content: str) -> bool:
            Takes the group_id and the content you want to post, return True 
            if the post has been successfully sent.
        '''
        #first step we should check if we can post to the group
        can_post_to_group = self.can_post_to_group(group_id=group_id)
        if not can_post_to_group:
            #the user does not has the permission to post to the specified group
            return False
        try:
            #step one: locate the write post component
            group_composer = self.driver.find_element_by_xpath('//div[contains(@data-pagelet,"GroupInlineComposer")]')
            #Step two: locate the button to open the edit text (Write something...)
            text_edit_button = group_composer.find_element(By.XPATH, './/div[contains(@role, "button")]')
            text_edit_button.click()
            #Wait until the write post modal become visible (max 10s)
            WebDriverWait(self.driver, 10).until(
                EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-describedby, "placeholder")]'))
            )
            #Select the text area
            text_area = self.driver.find_element_by_xpath('//div[contains(@aria-describedby, "placeholder")]')
            #Write the content
            text_area.click()
            text_area.send_keys(content)

            #locate the post button
            post_button = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Post")]')
            #submit the post
            post_button.click()
            #Wait until the modal disapear which means the post has been created
            WebDriverWait(self.driver, 15).until(
                EC.invisibility_of_element_located((By.XPATH, '//div[contains(@aria-label,"Post")]'))
            )
            return True
        except:
            #TODO - Add EVENT Logger
            return False

    def what_group_post_reaction(self, group_id=None, post_id=None, el_post=None):
        '''
            group_react_post(group_id: str, post_id: str, el_post: WebElement) -> str\n
            Takes the group_id and the post_id you want to react to or simply pass the webelement
            of the post, Return the reaction of the post, None if no reaction.
        '''
        if group_id is not None and post_id is not None:
            self.__is_it_facebook(
                #fallback url if we are not in facebook or if the facebook url is not the group url
                url=f"https://facebook.com/groups/{group_id}/posts/{post_id}",
                sub_url=f"/groups/{group_id}/posts/{post_id}"
            )
        #if the user provide a web element we should handle it in another way.
        elif el_post is not None:
            #TODO in further commit
            pass
        reactions = [
            LOVE_REACTION,
            LIKE_REACTION,
            CARE_REACTION,
            SAD_REACTION,
            ANGRY_REACTION,
            WOW_REACTION,
            HAHA_REACTION,
        ]
        for reaction in reactions:
            try:
                #if there is any remove {reaction} button this mean the user already has that reaction performed to the post
                self.driver.find_element_by_xpath(f'//div[contains(@aria-label, "Remove {reaction}")]')
                return reaction #return the specific reaction
            except:
                pass
        #if we reach this point this means the user has no reaction.
        return None
    
    def group_react_post(self, group_id=None, post_id=None, el_post=None, reaction='Like'):
        '''
            group_react_post(group_id: str, post_id: str, el_post: WebElement, reaction: enum<Like, Sad, Angry, Love, Haha>) -> bool\n
            Takes the group_id and the post_id you want to react to or simply pass the webelement
            of the post, and the reaction you want to perform, Return True if everything is fine.
        '''
        has_reaction = self.what_group_post_reaction(group_id=group_id, post_id=post_id, el_post=el_post)
        #if the user already has that reaction no need to re-perform it.
        if has_reaction is reaction:
            return True
        
        REACT_BTN_KEY_PATH = '//div[contains(@aria-label, "React")]'
        #if the user already has a reaction
        if has_reaction is not None:
            #we update the key of the reaction button
            REACT_BTN_KEY_PATH = f'//div[contains(@aria-label, "Change {has_reaction} reaction")]'
        
        try:
            #scroll down near the like button
            like_btn = self.driver.find_element_by_xpath(REACT_BTN_KEY_PATH)
            actions = ActionChains(self.driver)
            actions.move_to_element(like_btn).perform()
            #click the button to open the reaction list
            self.driver.execute_script("arguments[0].click();", like_btn)
            #Wait for the target reaction button to appear (10s max)
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((
                By.XPATH, f'//div[@aria-label="{reaction}"]'
            )))
            #locate the desired reaction button
            reaction_button = self.driver.find_element_by_xpath(f'//div[@aria-label="{reaction}"]')
            reaction_button.click()
            #wait until the reaction button disapear
            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((
                By.XPATH, f'//div[@aria-label="{reaction}"]'
            )))
            return True
        except Exception as e:
            #TODO - Add event logger
            return False

    def group_remove_interaction_with_post(self, group_id=None, post_id=None, el_post=None):
        '''
            group_remove_interaction_with_post(group_id: str, post_id: str, el_post: WebElement) -> bool\n
            Takes the group_id and the post_id you want to react to or simply pass the webelement
            of the post, Return True if the reaction has been removed.
        '''
        has_reaction = self.what_group_post_reaction(group_id=group_id, post_id=post_id, el_post=el_post)
        #if the user already has no reaction no need to perform it.
        if has_reaction is None:
            return True
        REACT_BTN_KEY_PATH = f'//div[contains(@aria-label, "Remove {has_reaction}")]'
        try:
            #locate the remove reaction button.
            reaction_btn = self.driver.find_element_by_xpath(REACT_BTN_KEY_PATH)
            #move the the button
            actions = ActionChains(self.driver)
            actions.move_to_element(reaction_btn).perform()
            #remove reaction button click
            reaction_btn.click()
            #wait until the default Like button appear.
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((
                By.XPATH, '//div[@aria-label="Like"]'
            )))
            return True
        except Exception as e:
            return False
    
    def can_comment_post_in_group(self, group_id=None, post_id=None, el_post=None):
        '''
            write_comment_to_group_post(group_id: str, post_id: str, el_post: WebElement, content: str) -> bool\n
            Takes the group_id and the post_id you want to react to or simply pass the webelement
            of the post, Return True if the user has the permission to write comment(comment area available).
        '''
        if group_id is not None and post_id is not None:
            self.__is_it_facebook(
                #fallback url if we are not in facebook or if the facebook url is not the group url
                url=f"https://facebook.com/groups/{group_id}/posts/{post_id}",
                sub_url=f"/groups/{group_id}/posts/{post_id}"
            )
        #if the user provide a web element we should handle it in another way.
        elif el_post is not None:
            #TODO in further commit
            pass
        
        try:
            #try to locate the comment box, if it pass this means we can make a comemnt
            self.driver.find_element_by_xpath('//div[contains(@aria-label, "Write a comment")]')
            return True
        except:
            #TODO - ADD EVENT LOGGER
            return False

    def write_comment_to_group_post(self, group_id=None, post_id=None, el_post=None, content=None):
        '''
            write_comment_to_group_post(group_id: str, post_id: str, el_post: WebElement, content: str) -> bool\n
            Takes the group_id and the post_id you want to react to or simply pass the webelement
            of the post, and the comment you want to write, Return True if everything is fine.
        '''
        can_post_comment = self.can_comment_post_in_group(group_id=group_id, post_id=post_id)
        if not can_post_comment:
            return False
        
        try:
            #locate comment box
            comment_box = self.driver.find_element_by_xpath('//div[contains(@aria-label, "Write a comment")]')
            #scroll down to the comment box
            actions = ActionChains(self.driver)
            actions.move_to_element(comment_box).perform()

            #write our comment
            comment_box.send_keys(content)
            #Hit enter to submit the comment
            comment_box.send_keys(Keys.ENTER)
            #TODO - solve this by finding a way to  make sure the comment has been posted
            time.sleep(2)
            return True
        except:
            #TODO - ADD EVENT LOGGER
            return False

    def scroll_group(self, group_id=None, num_of_post=10, time_between_post=4):
        '''
            scroll_group(group_id: str, num_of_post: int, time_between_post: int) -> List<WebElement>:
            Take the group id you want to scroll, the number of post to extract, and the time to sleep between each post,
            Return a list of WebElement (each element is a post) that can be used later with post interaction functions.
        '''
        #make sure we are in the page of the group with chronological order
        self.__is_it_facebook(
            #fallback url if we are not in facebook or if the facebook url is not the group url
            url=f"https://facebook.com/groups/{group_id}?sorting_setting=CHRONOLOGICAL", 
            sub_url=f"/groups/{group_id}?sorting_setting=CHRONOLOGICAL"
        )
        try:
            #wait until the feed load the posts
            WebDriverWait(self.driver, 30).until(EC.visibility_of_element_located((
                By.XPATH, '//div[@role="feed"]' 
            )))
            #first step let's locate the feed area of the group
            group_feed = self.driver.find_element_by_xpath('//div[@role="feed"]')
            actions = ActionChains(self.driver)
            actions.move_to_element(group_feed).perform()
            #extract the number of post we need
            return self.__extract_n_post(num_of_post=num_of_post, feed_element=group_feed)
        except:
            return []

    #  ------------  PAGE INTERACTION FUNCS  -------------  #
    def is_fan_of_page(self, page_uname=None):
        '''
            is_fan_of_page(page_uname: str) -> bool:
            Takes the username of the page you want to check and return True if the user already like it.
        '''
        self.__is_it_facebook(
            #fallback url if we are not in facebook or if the facebook url is not the group url
            url=f"https://facebook.com/{page_uname}", 
            sub_url=f"/{page_uname}"
        )
        try:
            #try to locate the "Liked" button which if present indicate the user already like the page
            self.driver.find_element_by_xpath('//div[@aria-label="Liked"]')
            return True
        except:
            #TODO - Add Event logger
            return False

    def like_page(self, page_uname=None):
        '''
            is_fan_of_page(page_uname: str) -> bool:\n
            Takes the username of the page you want to like and return True if the operation was performed correctly.
        '''
        #check if the user is already a fan of the page
        like_page = self.is_fan_of_page(page_uname=page_uname)
        #if the page is already liked, there is no need to move further.
        if like_page:
            return True

        try:
            #try to locate the like button
            like_btn = self.driver.find_element_by_xpath('//div[@aria-label="Like"]')
            like_btn.click()
            #Wait until the liked button appear
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((
                By.XPATH, '//div[@aria-label="Liked"]'
            )))
            return True
        except:
            #TODO - Add Event Logger
            return False

    def scroll_page(self, page_uname=None, num_of_post=10):
        '''
            scroll_page(page_uname: str, num_of_post: int) -> List<WebElement>:
            Take the page username you want to scroll, the number of post to extract, and the time to sleep between each post,
            Return a list of WebElement (each element is a post) that can be used later with post interaction functions.
        '''
        self.__is_it_facebook(
            #fallback url if we are not in facebook or if the facebook url is not the group url
            url=f"https://facebook.com/{page_uname}", 
            sub_url=f"/{page_uname}"
        )
        #extract num of posts
        return self.__extract_n_post(num_of_post=num_of_post)
        
    # ------------- POST HANDLER -------------  #
    def what_kind(self, el=None):
        '''
        what_kind(el: WebElement) -> (ERR_GET_TYPE, VIDEO_POST, PICTURE_POST, TEXT_POST, TEXT_BG_POST)\n
        this function take a web element which is a reference for specifc post (must be visible otherwise it will return ERR_GET_TYPE)
        and then return the type of the post (we can add further types in the future.)   
        '''
        if not el.is_displayed():
            return ERR_GET_TYPE

        try:
            #go to the element we want to analyse
            actions = ActionChains(self.driver)
            actions.move_to_element(el).perform()
            #extract the content area
            content_div = el.find_element(By.XPATH, './/div[1]/div[1]/div[1]/div[1]/div[1]/div[2]/div[1]/div[3]')

            try:
                #check if there is a play video button, if it didn't raise any exception the post is a video
                is_there_play_button = content_div.find_element(By.XPATH, './/div[@aria-label="Play video"]')
                return VIDEO_POST
            except:
                pass
        
            try:
                #extract all elements
                all_links = content_div.find_elements(By.XPATH, './/a[@role="link"]')
                for link in all_links:
                    #check if there is a photos this mean that the post is either one/many photos
                    href = link.get_attribute('href')
                    if "/photos/" in href:
                        return PICTURE_POST
            except:
                pass

            try:
                #check if there is a data-ad-preview (this mean it's an only text post)
                preview_message = content_div.find_element(By.XPATH, './/div[@data-ad-preview="message"]')
                return TEXT_POST
            except:
                pass

            return TEXT_BG_POST
        except:
            return ERR_GET_TYPE

    def toggle_play(self, el=None):
        '''
        toggle_play(el: WebElement) -> bool\n
        this function will toggle the play§/pause button on the webelemnt you pass, or the current page.
        if the video is in pause it will play, if the video is playing it will pause it and return True, if it return None
        this means the element is no more displayed or the current page is not a video page.
        '''
        current_status = self.is_playing(el=el)
        if current_status is None:
            #no video is being displayed already or the element is not visible.
            return None

        try:
            #if we pass an element
            if el is not None:
                #go to the element we want to analyse
                actions = ActionChains(self.driver)
                actions.move_to_element(el).perform()
            #tyr to locate the play video button
            try:
                play_btn_xpath = None
                #if the video is being played we search for the pause
                if current_status:
                    play_btn_xpath = '//div[contains(@aria-label, "Pause")]'
                else:
                    #else we search for the play button
                    play_btn_xpath = '//div[contains(@aria-label, "Play")]'
                
                #check if there is a play video button, if it didn't raise any exception the post is a video
                if el:
                    #we search locally so we need to add the dot before the xpath
                    play_button = el.find_element(By.XPATH, f'.{play_btn_xpath}')
                else:
                    #we search in the whole page
                    play_button = self.driver.find_element_by_xpath(play_btn_xpath)
                #click the play/pause button
                play_button.click()
                
                return not True
            except:
                return None
        except:
            return None

    def is_playing(self, el=None):
        '''
        is_playin(el: WebElement) -> bool \n
        return the status of the video being displayed of the element you pass (facebook post): it can be True or Flase, if it returns None this
        means the element is no more visible on the screen of the current page is not a video page.
        '''
        #if the element in the param is not visible and there is no already full screen active video
        if not el.is_displayed() and "/videos" not in self.driver.current_url:
            return None

        try:
            #try to locate the pause button, (if it does not raise any issue the video is playing already)
            if el:
                play_button = el.find_element(By.XPATH, './/div[contains(@aria-label, "Pause")]')
            else:
                play_button = self.driver.find_element_by_xpath('//div[contains(@aria-label, "Pause")]')
            return True
        except:
            return False

    def current_time(self, el=None):
        '''
        current_time(el: WebElement) -> int:\n
        this function return the current time  played in seconds of the video being displayed or the web element you pass (post).
        '''
        try:
            progress_bar = el.find_element(By.XPATH, './/div[@aria-label="Change Position"]')
            value = progress_bar.get_attribute('aria-valuenow')
            return round(float(value))
        except:
            return None

    def total_time(self, el=None):
        '''
        total_time(el: WebElement) -> int:\n
        this function return the total time in seconds of the video being displayed or the web element you pass (post).
        '''
        try:
            progress_bar = el.find_element(By.XPATH, './/div[@aria-label="Change Position"]')
            value = progress_bar.get_attribute('aria-valuemax')
            return round(float(value))
        except:
            return None

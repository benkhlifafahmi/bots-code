import time, re
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

class FacebookClient():
    driver = None
    def __init__(self, session_path=None):
        options = webdriver.ChromeOptions()
        if session_path is not None:
            options.add_argument('--user-data-dir='+session_path)
        #options.add_argument('--headless')
        options.add_argument("--disable-notifications")
        options.add_argument('--window-size=1920,1080')
        chromedriver_path = ChromeDriverManager().install()
        self.driver = webdriver.Chrome(chromedriver_path, options=options)

    def login(self, username=None, password=None):
        self.driver.get('https://facebook.com/')
        try:
            username_input = self.driver.find_element_by_id("email")
            password_input = self.driver.find_element_by_id("pass")
            submit   = self.driver.find_element_by_css_selector("button[name='login']")
            if username_input and password_input and submit:
                username_input.send_keys(username)
                password_input.send_keys(password)
                submit.click()
                WebDriverWait(self.driver, 15).until(EC.url_changes(self.driver.current_url))
        except:
            print('seems you are already logged in')

    def write_post_to_feed(self, content=None, media_path=None):
        if 'facebook.com' not in self.driver.current_url:
            self.driver.get('https://facebook.com/')
        try:
            #go to personal profile
            self.driver.execute_script("window.location='/me'")
            #wait till the url change
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@data-pagelet,"ProfileComposer")]/div/div/div/div/div[1]/div')))
            #search for the profile composer area
            profile_composer = self.driver.find_element_by_xpath('//div[contains(@data-pagelet,"ProfileComposer")]/div/div/div/div/div[1]/div')
            #open the modal to create a new post
            self.driver.execute_script("arguments[0].click();", profile_composer)
            #wait for the modal to load 
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-describedby, "placeholder")]')))
            text_area = self.driver.find_element_by_xpath('//div[contains(@aria-describedby, "placeholder")]')
            text_area.click()
            text_area.send_keys(content)
            time.sleep(3)
            submit_btn = self.driver.find_element_by_css_selector('div[aria-label="Post"]')
            submit_btn.click()
            WebDriverWait(self.driver, 10).until(EC.invisibility_of_element_located((By.CSS_SELECTOR, 'div[aria-label="Post"]')))
            return True          
        except Exception as e:
            print(e)
            print('[-] Error : cannot locate personal profile link')

    def join_group(self, group_id=None):
        self.driver.get('https://facebook.com/groups/'+group_id)
        try:
            try:
                join_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Join group")]')
                join_btn.click()
                WebDriverWait(self.driver, 10).until(lambda driver: driver.find_elements(By.XPATH,'//div[contains(@aria-label,"Joined")]') or driver.find_elements(By.XPATH,'//div[contains(@aria-label,"Cancel request")]'))
                return True
            except:
                print('Was not able to locate the join button maybe you\'ve already joined the group')
            
            try:
                join_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Cancel request")]')
                print('already joined the group, and the request is pending')
                return True
            except:
                print('cannot even locate the exit group button')
            
            try:
                join_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Joined")]')
                print('You have already joined this group')
                return True
            except:
                print('cannot even locate the exit group button')
            
        except:
            print('[+] Error joining this group')

    def leave_group(self, group_id=None):
        self.driver.get('https://facebook.com/groups/'+group_id)
        try:
            try:
                join_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Join group")]')
                print('Oops you are not a member of this group  ')
                return True
            except:
                print('Was not able to locate the join button maybe you\'ve already joined the group')
            
            try:
                cancel_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Cancel request")]')
                cancel_btn.click()
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-label,"Join group")]')))
                return True
            except:
                print('cannot even locate the exit group button')
            
            try:
                join_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Joined")]')
                join_btn.click()
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@role, "menuitem")]')))
                leave_btn = self.driver.find_element_by_xpath('//div[contains(@role,"menuitem")][3]')
                leave_btn.click()
                WebDriverWait(self.driver, 10).until(lambda driver: driver.find_elements(By.XPATH,'//div[contains(@aria-label,"Leave Group")]') or driver.find_elements(By.XPATH,'//div[contains(@aria-label,"Join group")]'))
                try:
                    confirm_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label,"Leave Group")]')
                    confirm_btn.click()
                except:
                    print('no need for confirmation of exit')
                WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-label,"Join group")]')))
                return True
            except:
                print('cannot even locate the exit group button')
            
        except:
            print('[+] Error joining this group')

    def can_post_to_group(self, group_id=None):
        self.driver.get('https://facebook.com/groups/'+group_id)
        try:
            self.driver.find_element_by_xpath('//div[contains(@data-pagelet,"GroupInlineComposer")]/div/div/div/div[1]/div')
            return True
        except:
            return False

    def write_post_to_group(self, group_id=None, content=None):
        self.driver.get('https://facebook.com/groups/'+group_id)
        try:
            group_composer = self.driver.find_element_by_xpath('//div[contains(@data-pagelet,"GroupInlineComposer")]/div/div/div/div[1]/div')
            self.driver.execute_script("arguments[0].click();", group_composer)
            #wait till the url change
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-describedby, "placeholder")]')))
            text_area = self.driver.find_element_by_xpath('//div[contains(@aria-describedby, "placeholder")]')
            text_area.click()
            text_area.send_keys(content)
            
            submit_btn = self.driver.find_element_by_css_selector('div[aria-label="Post"]')
            submit_btn.click()
            WebDriverWait(self.driver, 15).until(EC.invisibility_of_element_located((By.XPATH, '//div[contains(@aria-label, "Post")]')))
            return True
        except:
            print('an error occured while posting to the target group')

    def extract_posts_in_group(self, group_id=None, num_of_post=10, time_between_post=4):
        self.driver.get('https://facebook.com/groups/'+group_id+'?sorting_setting=RECENT_ACTIVITY')
        posts = []
        try:
            action = ActionChains(self.driver)
            while len(posts) < num_of_post:
                article = self.driver.find_element_by_xpath('//div[contains(@aria-posinset, "'+str(len(posts) + 1)+'")]')
                loc = article.location
                size = article.size
                post_id = None
                time_link = article.find_element_by_xpath('.//div/div/div/div/div/div[2]/div/div[2]/div/div[2]/div/div[2]/span/span/span[2]/span/a')
                action.move_to_element(time_link).perform()
                time_link.send_keys(Keys.CONTROL+"C")
                html_content = time_link.get_attribute('href')
                result = re.findall(r'facebook.com\/groups\/'+group_id+'\/posts\/(\d+)/',str(html_content))
                if (len(result) > 0):
                    post_id = result[0]
                
                profile_link = article.find_element_by_xpath('.//a[contains(@aria-hidden, "true")]')
                action.move_to_element(profile_link).perform()
                profile_link.send_keys(Keys.CONTROL+"C")
                author_text = profile_link.find_element_by_xpath('.//a').get_attribute("aria-label")
                
                posts.append({
                    'id': post_id,
                    'author': author_text,
                    'elements': {
                        'post': article,
                        'time_link': time_link,
                        'profile_link': profile_link,
                    },
                })
                
                #scroll down to office
                self.driver.execute_script('window.scroll(arguments[0], arguments[1])', loc['x'], loc['y'] + size['height'])
                time.sleep(time_between_post)
                WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-posinset, "'+str(len(posts) + 1)+'")]'))) #wait for next post to apear or load
            return posts
        except Exception as e:
            print(e)
            print('An error occured while extracting the posts list')
            return posts

    def group_post_cursor_next(self, last_seen_element=None, num_of_post=10, time_betwen_post=4):
        pass
    
    def group_commet_post(self, group_id=None, post_id=None, content=None):
        self.driver.get('https://facebook.com/groups/'+group_id+'/posts/'+post_id)
        try:
            comment_section = self.driver.find_element_by_xpath('//div[contains(@aria-label, "Write a comment")]')
            comment_section.send_keys(content)
            comment_section.send_keys(Keys.ENTER)
            time.sleep(1)
            return True
        except Exception as e:
            print('Cannot comment this post')
        
    def group_react_post(self, group_id=None, post_id=None, reaction='Like'):
        self.driver.get('https://facebook.com/groups/'+group_id+'/posts/'+post_id)
        try:
            btn_react = self.driver.find_element_by_xpath('//div[contains(@aria-label, "React")]')
            self.driver.execute_script("arguments[0].click();", btn_react)
            WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@aria-label, "'+reaction+'")]')))
            reaction_btn = self.driver.find_element_by_xpath('//div[contains(@aria-label, "'+reaction+'")]')
            reaction_btn.click()
            time.sleep(1)
            return True
        except Exception as e:
            print(e)
            print('Cannot comment this post')
        

    def write_commet_to_post(self):
        pass

    def like_post(self):
        pass

    def search_facebook(self, term):
        pass

    def scroll_page(self):
        pass

    def watch_video(self):
        pass

    def close(self):
        self.driver.close()
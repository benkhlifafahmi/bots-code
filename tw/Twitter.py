import time, re
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains

class TwitterClient():
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
        try:
            self.driver.get('https://twitter.com/i/flow/login')
            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, '//input[contains(@autocomplete, "username")]')))
            current_url = self.driver.current_url

            username_input = self.driver.find_element_by_xpath('//input[contains(@autocomplete, "username")]')
            username_input.send_keys(username)
            username_input.send_keys(Keys.ENTER)

            WebDriverWait(self.driver, 15).until(EC.visibility_of_element_located((By.XPATH, '//input[contains(@autocomplete, "current-password")]')))
            password_input = self.driver.find_element_by_xpath('//input[contains(@autocomplete, "current-password")]')
            password_input.send_keys(password)
            password_input.send_keys(Keys.ENTER)
            WebDriverWait(self.driver, 15).until(lambda driver: driver.current_url != current_url)
        except:
            print('[-] Error logging in')

    def is_logged_in(self):
        if "twitter.com" not in self.driver.current_url:
            self.driver.get('https://twitter.com/')
        
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@data-testid, "SideNav_AccountSwitcher_Button")]')))
            menu_item = self.driver.find_element_by_xpath('//div[contains(@data-testid, "SideNav_AccountSwitcher_Button")]')
            if menu_item:
                return True
            else:
                return False
        except Exception as e:
            return False

    def get_trends(self):
        if "twitter.com" not in self.driver.current_url:
            self.driver.get('https://twitter.com/')
            time.sleep(3)
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@data-testid,"trend")]')))
        trends = []
        try:
            trends_sections = self.driver.find_elements_by_xpath('//div[contains(@data-testid,"trend")]')
            for trend in trends_sections:
                trend_span = trend.find_elements_by_xpath('.//span')
                if trend_span and len(trend_span) > 2:
                    trends.append({
                        'element': trend,
                        'text': trend_span[1].text
                    })
            return trends
        except Exception as e:
            return trends

    def walk_home(self, tweets_count=10):
        if "twitter.com" not in self.driver.current_url:
            self.driver.get('https://twitter.com/')
            time.sleep(3)
        if "Home" not in self.driver.title:
            home_link = self.driver.find_element_by_xpath('//a[contains(@data-testid, "AppTabBar_Home_Link")]')
            home_link.click()
        actions = ActionChains(self.driver)
        tweets = []
        try:
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//article[contains(@data-testid, "tweet")]')))
            while (len(tweets) < tweets_count):
                print('tweet lenght', len(tweets))
                tweets_list = self.driver.find_elements_by_xpath('//article[contains(@data-testid, "tweet")]')
                offset = len(tweets)%13
                for tweet in tweets_list[offset:]:
                    position = tweet.location
                    size = tweet.size
                    self.driver.execute_script('window.scroll(arguments[0], arguments[1])', position['x'], position['y'])

                    links = tweet.find_elements_by_xpath('.//a[contains(@role, "link")]')
                    username_link = links[1]
                    post_link = None
                    for link in links:
                        if "/status/" in link.get_attribute('href'):
                            post_link = link
                            break
                    tweets.append({
                        'elements': {
                            'tweet': tweet,
                            'post_link': post_link,
                            'username': username_link
                        },
                        'username': username_link.get_attribute('href').split('twitter.com/')[1],
                        'post_id': post_link.get_attribute('href').split('/')[-1],
                        'location': position,
                        'size': size,
                    })
                    
                    self.driver.execute_script('window.scroll(arguments[0], arguments[1])', position['x'], position['y']+size['height'])
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(3)
            return tweets
        except Exception as e:
            print(e)
            return tweets

    def get_more_tweets(self, previously_scrapped=0, tweets_count=10, last_element=None):
        if "twitter.com" not in self.driver.current_url:
            self.driver.get('https://twitter.com/')
            time.sleep(3)
        if "Home" not in self.driver.title:
            home_link = self.driver.find_element_by_xpath('//a[contains(@data-testid, "AppTabBar_Home_Link")]')
            home_link.click()
        actions = ActionChains(self.driver)
        tweets = []
        try:
            self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
            if last_element:
                self.driver.execute_script('window.scroll(arguments[0], arguments[1])', last_element['location']['x'], last_element['location']['y']+last_element['size']['height'])
                time.sleep(3)
            print('[+] start loading more')
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//article[contains(@data-testid, "tweet")]')))
            while (len(tweets) < tweets_count):
                tweets_list = self.driver.find_elements_by_xpath('//article[contains(@data-testid, "tweet")]')
                offset = (len(tweets) + previously_scrapped)%13
                print('total tweets found: ', len(tweets))
                for tweet in tweets_list[offset:]:
                    position = tweet.location
                    size = tweet.size
                    self.driver.execute_script('window.scroll(arguments[0], arguments[1])', position['x'], position['y'])
                    links = tweet.find_elements_by_xpath('.//a[contains(@role, "link")]')
                    username_link = links[1]
                    post_link = None
                    for link in links:
                        if "/status/" in link.get_attribute('href'):
                            post_link = link
                            break
                    tweets.append({
                        'elements': {
                            'tweet': post_link,
                            'username': username_link
                        },
                        'username': username_link.get_attribute('href').split('twitter.com/')[1],
                        'post_id': post_link.get_attribute('href').split('/')[-1],
                        'location': position,
                        'size': size,
                    })
                    
                    self.driver.execute_script('window.scroll(arguments[0], arguments[1])', position['x'], position['y']+size['height'])
                self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight)')
                time.sleep(3)
            return tweets
        except Exception as e:
            print('Exception', e)
            return tweets
    def close(self):
        self.driver.close()

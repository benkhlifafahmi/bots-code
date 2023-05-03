import time, re
from selenium import webdriver
from selenium.webdriver.common import keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains



class YoutubeClient():
    driver = None
    def __init__(self, session_path=None):
        options = webdriver.ChromeOptions()
        if session_path is not None:
            options.add_argument('--user-data-dir='+session_path)
        #options.add_argument('--headless')
        options.add_argument("--disable-notifications")
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--disable-web-security')
        options.add_argument('--allow-running-insecure-content')
        #chromedriver_path = ChromeDriverManager().install()
        self.driver = webdriver.Chrome('/usr/bin/chromedriver', options=options)
        #self.driver = webdriver.Remote("http://127.0.0.1:4444/wd/hub", options=options)
        #driver = webdriver.Remote(command_executor='http://%s:%s/wd/hub' %(SAUCE_USERNAME, SAUCE_ACCESS_KEY))
    def is_logged_in(self):
        if "youtube.com" not in self.driver.current_url:
            self.driver.get('https://youtube.com/')
        try:
            btn_avatar = self.driver.find_element_by_xpath('//button[contains(@id, "avatar-btn")]')
            if btn_avatar:
                return True
            else:
                return False
        except:
            return False
    def login(self, username, password):
        if "youtube.com" not in self.driver.current_url:
            self.driver.get('https://youtube.com/')
        else:
            home_link = self.driver.find_element_by_xpath('//a[contains(@id, "logo")]')
            home_link.click()
        time.sleep(2)
        btn_login = self.driver.find_element_by_xpath('//ytd-button-renderer[contains(@id, "sign-in-button")]')
        link_login = btn_login.find_element_by_xpath('.//a')
        link_login.click()
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//input[contains(@name, "identifier")]'))) 
        email_input = self.driver.find_element_by_xpath('//input[contains(@name, "identifier")]')
        email_input.send_keys(username)
        email_input.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//input[contains(@name, "password")]'))) 
        password_input = self.driver.find_element_by_xpath('//input[contains(@name, "password")]')
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//form[contains(@id, "search-form")]'))) 
        return True
    
    def hover(self, element):
        actions = ActionChains(self.driver)
        actions.move_to_element(element).perform()
    
    def watch_video(self, video_id=None, video_element=None, keep_the_last=4):
        total_seconds = self.open_video(video_id, video_element)
        print('video length is : ', total_seconds)
        while True:
            if self.is_ad_open():
                print('we have ads here you should wait for add to skip')
                self.skip_ads(after=2)
            total_seconds = self.get_total_play_time()
            current_play_time = self.get_current_play()
            if not self.is_playing():
                self.play_pause()
            print('We played : ', current_play_time, '/', total_seconds)
            if (int(current_play_time) > (int(total_seconds) - keep_the_last)):
                break
            time.sleep(2)
    
    def open_video(self, video_id=None, video_element=None):
        if video_id is not None:
            self.driver.get('https://www.youtube.com/watch/?v=%s'%(video_id)) #open the video link
        elif video_element is not None:
            video_link = video_element.find_element_by_xpath('.//a[contains(@id, "video-title")]')
            video_link.click()
        else:
            return ''
        WebDriverWait(self.driver, 5).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@class, "ytp-progress-bar")]'))) #wait for the slider to be located (video started playing or ads)
        progress_bar = self.driver.find_element_by_class_name('ytp-progress-bar')
        self.hover(progress_bar)
        total_seconds  = progress_bar.get_attribute('aria-valuemax')
        return total_seconds
    
    def get_total_play_time(self):
        progress_bar = self.driver.find_element_by_class_name('ytp-progress-bar')
        self.hover(progress_bar)
        total_seconds  = progress_bar.get_attribute('aria-valuemax')
        return total_seconds

    def is_playing(self):
        button_play = self.driver.find_element_by_class_name('ytp-play-button')
        btn_text = button_play.get_attribute('aria-label')
        return 'Pause' in btn_text

    def play_pause(self):
        button_play = self.driver.find_element_by_class_name('ytp-play-button')
        button_play.click()

    def get_current_play(self):
        progress_bar = self.driver.find_element_by_class_name('ytp-progress-bar')
        self.hover(progress_bar)
        total_seconds  = progress_bar.get_attribute('aria-valuenow')
        return total_seconds

    def like_video(self, video_id=None, video_element=None, remove_like=False):
        if video_id or video_element:
            self.open_video(video_id, video_element)
        actions_list = self.driver.find_element_by_xpath('//div[contains(@id, "top-level-buttons-computed")]')
        like_btn_container = actions_list.find_elements_by_xpath('.//ytd-toggle-button-renderer')[0]
        style = like_btn_container.get_attribute('style')
        like_btn = like_btn_container.find_element_by_xpath('.//a')
            
        if 'style-default-active' in style:
            print('[!] you have already liked this video')
            if remove_like:
                like_btn.click()
        else:
            like_btn.click()



    def dislike_video(self, video_id=None, video_element=None, remove_like=False):
        if video_id or video_element:
            self.open_video(video_id, video_element)
        actions_list = self.driver.find_element_by_xpath('//div[contains(@id, "top-level-buttons-computed")]')
        dislike_btn_container = actions_list.find_elements_by_xpath('.//ytd-toggle-button-renderer')[1]
        style = dislike_btn_container.get_attribute('style')
        dislike_btn = dislike_btn_container.find_element_by_xpath('.//a')
            
        if 'style-default-active' in style:
            print('[!] you have already liked this video')
            if remove_like:
                dislike_btn.click()
        else:
            dislike_btn.click()


    def is_subscribed(self, channel_id=None, video_id=None):
        try:
            if "youtube.com" not in self.driver.current_url:
                if channel_id is not None:
                    self.driver.get('https://www.youtube.com/channel/'+channel_id)
                elif video_id is not None:
                    self.driver.get('https://www.youtube.com/watch?v='+video_id)
            if not self.is_logged_in():
                print('[-] ERR/ you should login first in order to subscribe to a channel')
                return None
            if channel_id:
                if channel_id not in self.driver.current_url:
                    self.driver.get('https://www.youtube.com/channel/'+channel_id)
            elif video_id:
                if video_id not in self.driver.current_url:
                    self.driver.get('https://www.youtube.com/watch?v='+video_id)
            
            WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//tp-yt-paper-button[contains(@class, "ytd-subscribe-button-renderer")]'))) #wait for the subscribe/unsubscribe button to appear on the screen
            
            subscribe_btn = self.driver.find_element_by_xpath('//tp-yt-paper-button[contains(@class, "ytd-subscribe-button-renderer")]')
            return subscribe_btn.get_attribute('subscribed') is not None
        except:
            return False

    def subscribe_channel(self, channel_id=None, video_id=None):
        if "youtube.com" not in self.driver.current_url:
            if channel_id is not None:
                self.driver.get('https://www.youtube.com/channel/'+channel_id)
            elif video_id is not None:
                self.driver.get('https://www.youtube.com/watch?v='+video_id)
        if not self.is_logged_in():
            print('[-] ERR/ you should login first in order to subscribe to a channel')
            return None
        if channel_id:
            if channel_id not in self.driver.current_url:
                self.driver.get('https://www.youtube.com/channel/'+channel_id)
        elif video_id:
            if video_id not in self.driver.current_url:
                self.driver.get('https://www.youtube.com/watch?v='+video_id)
        
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//tp-yt-paper-button[contains(@class, "ytd-subscribe-button-renderer")]'))) #wait for the subscribe/unsubscribe button to appear on the screen
        
        subscribe_btn = self.driver.find_element_by_xpath('//tp-yt-paper-button[contains(@class, "ytd-subscribe-button-renderer")]')
        subscribe_btn.click()
        
    def unsubscribe_channel(self, channel_id=None, video_id=None):
        if "youtube.com" not in self.driver.current_url:
            if channel_id is not None:
                self.driver.get('https://www.youtube.com/channel/'+channel_id)
            elif video_id is not None:
                self.driver.get('https://www.youtube.com/watch?v='+video_id)
        if not self.is_logged_in():
            print('[-] ERR/ you should login first in order to subscribe to a channel')
            return None
        if channel_id:
            if channel_id not in self.driver.current_url:
                self.driver.get('https://www.youtube.com/channel/'+channel_id)
        elif video_id:
            if video_id not in self.driver.current_url:
                self.driver.get('https://www.youtube.com/watch?v='+video_id)
        
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//tp-yt-paper-button[contains(@class, "ytd-subscribe-button-renderer")]'))) #wait for the subscribe/unsubscribe button to appear on the screen
        
        subscribe_btn = self.driver.find_element_by_xpath('//tp-yt-paper-button[contains(@class, "ytd-subscribe-button-renderer")]')
        subscribe_btn.click()
        
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//tp-yt-paper-dialog[not(contains(@aria-hidden, "true"))]'))) #wait for the unsubscribe modal to appear
        modal_content = self.driver.find_element_by_xpath('//tp-yt-paper-dialog[not(contains(@aria-hidden, "true"))]')
        unsubscribe_btn = modal_content.find_element_by_xpath('.//yt-button-renderer[contains(@id, "confirm-button")]/a')
        unsubscribe_btn.click()

    def skip_ads(self, after=1):
        try:
            WebDriverWait(self.driver, 10).until(lambda driver: 'none' not in driver.find_element_by_class_name('ytp-ad-skip-button-container').get_attribute('style'))
            skip_ad_btn = self.driver.find_element_by_class_name('ytp-ad-skip-button')
            time.sleep(after)
            skip_ad_btn.click()
        except Exception as e:
            print(e)
            return None

    def is_ad_open(self):
        try:
            skip_ad_btn = self.driver.find_element_by_class_name('ytp-ad-skip-ad-slot')
            if skip_ad_btn:
                return True
            else:
                return False
        except:
            return False

    def search_youtube(self, term):
        if 'youtube.com' not in self.driver.current_url:
            self.driver.get('https://www.youtube.com/')
        current_url = self.driver.current_url
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.ID, 'search-form')))
        search_input = self.driver.find_element_by_xpath('//input[contains(@id, "search")]')
        search_input.send_keys(term)
        search_input.send_keys(Keys.ENTER)
        WebDriverWait(self.driver, 10).until(EC.visibility_of_element_located((By.XPATH, '//div[contains(@id, "filter-menu")]')))
        section_list = self.driver.find_element_by_tag_name('ytd-search')
        video_renders = section_list.find_elements_by_xpath('.//ytd-video-renderer')
        result = []
        for video in video_renders:
            video_link = video.find_element_by_xpath('.//a[contains(@id, "video-title")]')
            title = video_link.get_attribute('title')
            link = video_link.get_attribute('href')
            
            location = video.location
            size = video.size
            result.append({
                'title': title,
                'link': link,
                'cord': {
                    'location': location,
                    'width': size['width'],
                    'height': size['height'],
                },
                'web_element': video,
            })
        return result
    
    def get_more_results(self, last_position=None):
        if last_position == None:
            return []
        self.driver.execute_script('window.scrollTo(arguments[0], arguments[1])', last_position['x'], last_position['y'])
        section_list = self.driver.find_element_by_tag_name('ytd-search')
        video_renders = section_list.find_elements_by_xpath('.//ytd-video-renderer')
        result = []
        for video in video_renders:
            video_link = video.find_element_by_xpath('.//a[contains(@id, "video-title")]')
            title = video_link.get_attribute('title')
            link = video_link.get_attribute('href')
            
            location = video.location
            size = video.size
            result.append({
                'title': title,
                'link': link,
                'cord': {
                    'location': location,
                    'width': size['width'],
                    'height': size['height'],
                },
                'web_element': video,
            })
        return result


    def load_comments(self):
        pass

    def more_comments(self):
        pass

    def load_comment_replies(self):
        pass

    def more_comment_replies(self):
        pass

    def comment_video(self):
        pass

    def reply_comemnt(self):
        pass

    def like_comment(self):
        pass

    def dislike_comment(self):
        pass

    def close(self):
        self.driver.close()
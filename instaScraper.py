from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import sys
import os
import requests
import shutil

class Scraper:
    def __init__(self, username, password, target_username):
        self.username = username
        self.password = password
        self.target_username = target_username
        self.base_path = os.path.join('data', self.target_username) # change it as per requirement
        self.imagesData_path = os.path.join(self.base_path, 'images') # change it as per requirement 
        self.descriptionsData_path = os.path.join(self.base_path, 'descriptions') # change it as per requirement
        self.driver = webdriver.Chrome('chromedriver') # I'm using linux. You can change it as per your OS.
        self.main_url = 'https://www.instagram.com'
        
        # check the internet connection and if the home page is fully loaded or not. 
        try:
            self.driver.get(self.main_url)
            WebDriverWait(self.driver, 10).until(EC.title_is('Instagram'))
        except TimeoutError:
            print('Loading took too much time. Please check your connection and try again.')
            sys.exit()
        

        self.login()
        self.close_dialog_box()
        self.open_target_profile()

        # check if the directory to store data exists
        if not os.path.exists('data'):
            os.mkdir('data')
        if not os.path.exists(self.base_path):
            os.mkdir(self.base_path)
        if not os.path.exists(self.imagesData_path):
            os.mkdir(self.imagesData_path)
        
        self.download_posts()
        self.driver.close()


    def login(self):
        try :
            
            sleep(2)
            username_input = self.driver.find_element_by_css_selector("input[name='username']")
            password_input = self.driver.find_element_by_css_selector("input[name='password']")
            
            username_input.send_keys(self.username)
            password_input.send_keys(self.password)
            
            
            login_button =  self.driver.find_element_by_xpath("//button[@type='submit']")
            login_button.click()
            
            sleep(5)
        except Exception:
            print('Please try again with correct credentials or check your connection.')

        print('Login Successful!')
        

    def close_dialog_box(self):
        ''' Close the Notification Dialog '''
        try:
            close_btn = self.driver.find_element_by_xpath('//button[text()="Not Now"]')
            close_btn.click()
        except Exception:
            pass 


    def open_target_profile(self):  
        target_profile_url  = self.main_url + '/' + self.target_username
        print('Redirecting to {0} profile...'.format(self.target_username))
        
        # check if the target user profile is loaded. 
        try:
            self.driver.get(target_profile_url) 
            WebDriverWait(self.driver, 10).until(EC.title_contains(self.target_username))
        except TimeoutError:
            print('Some error occurred while trying to load the target username profile.')
            sys.exit()  
        

    def load_fetch_posts(self):
        '''Load and fetch target account posts'''

        image_list = [] # to store the posts

        # get the no of posts
    
        try:
            r = requests.get(self.main_url + '/' + self.target_username)
            s = BeautifulSoup(r.text, "html.parser") 
	
        	# finding meta info 
            meta = s.find("meta", property ="og:description")  
            
            s = meta.attrs['content']
            #splittting the content 
        	# then taking the first part 
            s = s.split("-")[0] 
        	
        	# again splitting the content 
            s = s.split(" ") 
        	
        	# assigning the values 
            self.Followers = s[0] 
            self.Following = s[2] 
            self.no_of_posts = int(s[4])  
        except Exception:
            print('Some exception occurred while trying to find the number of posts.')
            sys.exit()
    

        try:
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            all_images = soup.find_all('img', attrs = {'class': 'FFVAD'}) 
        
            for img in all_images:
                if img not in image_list:
                    image_list.append(img)

            if self.no_of_posts > 12: # 12 posts loads up when we open the profile
                no_of_scrolls = round(self.no_of_posts/12) + 6 # extra scrolls if any error occurs while scrolling.

                # Loading all the posts
                print('Loading all the posts...')
                for __ in range(no_of_scrolls):
                    
                    # Every time the page scrolls down we need to get the source code as it is dynamic
                    self.driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                    sleep(2) # introduce sleep time as per your internet connection as to give the time to posts to load
                    
                    soup = BeautifulSoup(self.driver.page_source, 'lxml')
                    all_images = soup.find_all('img') 
        
                    for img in all_images:
                        if img not in image_list:
                            image_list.append(img)
        
        except Exception:
            print('Some error occurred while scrolling down and trying to load all posts.')
            sys.exit()  
        
        return image_list


    def download_posts(self):
        ''' To download all the posts of the target account ''' 

        image_list = self.load_fetch_posts()
        no_of_images = len(image_list)
        for index, img in enumerate(image_list, start = 1):
            try :    
                filename = 'image_' + str(index) + '.jpg'
                image_path = os.path.join(self.imagesData_path, filename)
                link = img.get('src')
                response = requests.get(link, stream = True)
                print('Downloading image {0} of {1}'.format(index, no_of_images))
            
                with open(image_path, 'wb') as file:
                    shutil.copyfileobj(response.raw, file)
            except :
                pass 
        print('Download completed!')

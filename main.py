import getpass # for hiding the password while typing
from instaScraper import Scraper 

if __name__ == '__main__':

    print('Enter the username and password of your Instagram Account')
    print("the password will not be visible for your security purpose you just type it without error")
    username = input('Username: ') # input your username
    password = getpass.getpass() # input your password
    
    print("Enter the username of the target whose photos and descriptions you want to download from")
    print("    target_username must fulfill either or both of the below two criteria:")
    print("    -> You must follow that account")
    print("    -> It must be an open account.")

    target_username = input('Target Username: ') # Enter the username of the account you want to scrap photos and capions from 
    scraper = Scraper(username, password, target_username) # Instagram Scraper Object
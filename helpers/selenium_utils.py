from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import os
from time import sleep

class SeleniumBrowser:
    def __init__(self, driver_path=''):
        init_path = os.path.dirname(os.path.realpath(__file__))
        self.driver_path = driver_path if driver_path else '{}/../assets/chromedriver.exe'.format(init_path)
        ublock_origin = '{}/../assets/uBlock0.chromium'.format(init_path)
        chrome_options = Options()
        chrome_options.add_argument('load-extension=' + ublock_origin)
        caps = DesiredCapabilities().CHROME
        caps["pageLoadStrategy"] = "none"
        self.chrome = webdriver.Chrome(executable_path=self.driver_path, chrome_options=chrome_options, desired_capabilities=caps)
        self.chrome.create_options()
    
    def open_link(self, link, cookies_domain, keys):
        cookies = {}
        self.chrome.get(link)
        foundElement = False
        while not foundElement:
            try:
                self.chrome.find_element_by_id('selectReadType')
                foundElement = True
            except:
                sleep(0.1)
        user_agent = self.chrome.execute_script("return navigator.userAgent;")
        for cookie in self.chrome.get_cookies():
            if cookie['domain'] in cookies_domain and cookie['name'] in keys:
                cookies[cookie['name']] = cookie['value']
        self.chrome.quit()
        return cookies, user_agent
from selenium import webdriver
import os
from time import sleep

def DesiredCapabilities(type):
    if type == "Firefox":
        return {
        "browserName": "firefox",
        "marionette": True,
        "acceptInsecureCerts": True,
        "pageLoadStrategy" : "none"
        }
    if type == "Edge":
        return {
        "browserName": "MicrosoftEdge",
        "version": "",
        "platform": "WINDOWS",
        "pageLoadStrategy" : "none"
        }
    if type == "Chrome":
        return {
        "browserName": "MicrosoftEdge",
        "version": "",
        "platform": "WINDOWS",
        "pageLoadStrategy" : "none"
        }
    else:
        raise Exception("Wrong Browser Type") 

class SeleniumBrowser:
    def __init__(self, browsertype="Chrome", driver_path=''):
        init_path = os.path.dirname(os.path.realpath(__file__))
        self.driver_path = driver_path if driver_path else '{}/../assets/chromedriver.exe'.format(init_path)
        options = getattr(webdriver, browsertype.lower()).options.Options()
        if browsertype == "Chrome":
            ublock_origin_chrome = '{}/../assets/uBlock0.chromium'.format(init_path)
            options.add_argument('load-extension=' + ublock_origin_chrome)
        caps = DesiredCapabilities(browsertype)
        self.browser = getattr(webdriver, browsertype)(executable_path=self.driver_path, options=options, desired_capabilities=caps)
        self.browser.create_options()
    
    def open_link(self, link, cookies_domain, keys):
        cookies = {}
        self.browser.get(link)
        foundElement = False
        while not foundElement:
            try:
                self.browser.find_element_by_id('selectReadType')
                foundElement = True
            except:
                sleep(0.1)
        user_agent = self.browser.execute_script("return navigator.userAgent;")
        for cookie in self.browser.get_cookies():
            if cookie['domain'] in cookies_domain and cookie['name'] in keys:
                cookies[cookie['name']] = cookie['value']
        self.browser.quit()
        return cookies, user_agent
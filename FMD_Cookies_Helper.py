import cloudscraper #https://github.com/VeNoMouS/cloudscraper
import json
import argparse
from html.parser import HTMLParser
import re
import inquirer
from helpers.selenium_utils import *
from playwright.sync_api import sync_playwright



CONFIG_PATH = "config.json"
KEYS = ['__cfduid','cf_clearance']
WEBSITES = {
        'toonily' : {
            'url': "https://toonily.com/",
            'domain' : ".toonily.com",
            'modules_uuid' : '1bc39e1bc5e64c12989c051fe3932d4d',
            'element_to_wait' : 'PLACEHOLDER_1'
        }
    }

class CFScraper:
    def __init__(self):
        self.sc = cloudscraper.create_scraper()

    def get_from_cloudscraper(self, site):
        url = WEBSITES.get(site)['url']
        domain = WEBSITES.get(site)['domain']
        cookies = {}
        user_agent = ""
        try:
            _ = self.sc.get(url)
            for key in KEYS:
                cookies[key] = self.sc.cookies.get(key, '', domain=domain)
            user_agent = self.sc.headers['User-Agent']
        except Exception as e:
            print("Unable to fetch data from site (try updating cloudscraper dependency with \"pip install -U cfscrape\").")
            print("Error message: {}".format(e))
        return cookies, user_agent

def pass_to_fmd(modules_path, uuid, cookies, user_agent):
    print("Exporting {}'s cookies to FMD's settings".format(uuid))
    cookie_string = ";".join([str(key)+"="+str(val) for key,val in cookies.items()])
    try:
        with open(modules_path, 'r+') as f:
            data = json.load(f)
            for i in data:
                if i['ID'] == uuid:
                    i['Cookies'] = [] #Wipe FMD2's weird cookiejar
                    i['Settings']['Enabled'] = True
                    i['Settings']['HTTP']['Cookies'] = cookie_string
                    i['Settings']['HTTP']['UserAgent'] = user_agent
                    break
            f.seek(0)
            json.dump(data, f, ensure_ascii=False)
            f.truncate()
        print("\tSettings exported")
    except:
        print("Error : Unable to open modules.json. Put this script in the same folder or specify it's path in config.json")


def create_default_config(modules_path = ""):
    config = {}
    config["METHOD"] = "cloudscraper"
    config["WEBSITE_DEFAULT"] = None
    config["MODULES.JSON_PATH"] = modules_path if modules_path != "" else  "modules.json"
    config["DONT_ASK_AGAIN"] = False 
    save_config(config)
    return config

def save_config(config):
    with open(CONFIG_PATH, "w") as write_file:
        json.dump(config, write_file, indent=4, sort_keys=True)


def open_config():
    with open(CONFIG_PATH, "r") as read_file:
        return json.load(read_file)

def get_cookies_browser(site, context):
    url = WEBSITES.get(site)['url']
    domain = WEBSITES.get(site)['domain']

    cookies = {}
    user_agent = ""

    page = context.new_page()
    page.goto(url)

    element = WEBSITES.get(site)['element_to_wait']
    result = page.wait_for_selector(element, timeout=30)

    if result is None:
        raise Exception #add custom exception

    for cookie in context.cookies():
        if cookie['domain'] == domain and cookie['name'] in KEYS:
            cookies[cookie['name']] = cookie['value']

    return cookies, user_agent
        


def main():
    print("Welcome to FMD Cloudflare helper!")

    config = {}
    task = {}

    try:
        print("Opening saved configurations.")
        config = open_config()
    except Exception as _:
        print("Unable to open saved configurations\n Creating {}.".format(CONFIG_PATH))
        config = create_default_config()

    if config["DONT_ASK_AGAIN"]:
        task = {
                'method' : config['METHOD'],
                'websites' : config["WEBSITE_DEFAULT"]
                }
    else:
        task = inquirer.prompt([
            inquirer.List('method',
                        message="Do you want to use your browser or automated cloudflare scraper (cloudscraper)?",
                        choices=['chrome', 'firefox', 'cloudscraper'],
                        default=config["METHOD"],
                    ),
            inquirer.Checkbox('websites',
                        message="Select websites you want to travel on (right arrow to select)",
                        choices=['toonily', 'mangasee'],
                        default=config["WEBSITE_DEFAULT"],
                    ),
            inquirer.List('ask',
                        message="Do you want this script to remember your choices and never ask again?",
                        choices=['Yes', 'No'],
                        default='No',
                    )
        ])
        config["METHOD"] = task['method']
        config["WEBSITE_DEFAULT"] = task['websites']
        config["DONT_ASK_AGAIN"] = task['ask']
        save_config(config)

    if len(task['websites']) > 0:
        print("Updating cookies")

        if task['method'] == "chrome" or task['method'] == "firefox":
            with sync_playwright() as p:
                if task['method'] == "chrome":
                    browser = p.chromium.launch(headless=False)
                else:
                    browser = p.firefox.launch(headless=False)
                context = browser.new_context()
                for website in task['websites']:
                    print("> {}".format(website))
                    cookies, user_agent = get_cookies_browser(website, context)
                    if len(cookies) > 0:
                        pass_to_fmd(config['MODULES.JSON_PATH'], WEBSITES.get(website)['modules_uuid'], cookies, user_agent)
                browser.close()


        elif task['method'] == "cloudscraper":
            cfscraper = CFScraper()
            for website in task['websites']:
                print("> {}".format(website))
                cookies, user_agent = cfscraper.get_from_cloudscraper(website)
                if len(cookies) > 0:
                    pass_to_fmd(config['MODULES.JSON_PATH'], WEBSITES.get(website)['modules_uuid'], cookies, user_agent)
    print("Finished!")

if __name__ == "__main__":
    main()
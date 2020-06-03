import cloudscraper #https://github.com/VeNoMouS/cloudscraper
import json
from time import sleep
from random import randint
import argparse
from html.parser import HTMLParser
import re
import browser_cookie3
import subprocess
import os
import webbrowser
from time import sleep

class chko_parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.chko = ''

    def handle_data(self, data):
        if 'chko' in data:
            s_hex = re.findall(r'\[(.*?)\]', data)[0].replace('\"','')
            val = s_hex.encode().decode('unicode-escape')
            self.chko += val

class Scraper:
    def __init__(self):
        self.sc = cloudscraper.create_scraper()
    
    def get_from_browser(self, domain, browser_type):
        try:
            if browser_type == "firefox":
                cookie_jar = browser_cookie3.firefox(domain_name=domain)
            elif browser_type == "chrome":
                cookie_jar = browser_cookie3.chrome(domain_name=domain)
            cookies = {
                '__cfuid' : cookie_jar._cookies[".kissmanga.com"]["/"]["__cfduid"].value,
                'cf_clearance' : cookie_jar._cookies[".kissmanga.com"]["/"]["cf_clearance"].value
            }
            #Initiating Flask webapp
            p = subprocess.Popen("python \"{}\"".format(os.path.join(os.path.dirname(os.path.realpath(__file__)),'flask_server.py')),
                            stdout=subprocess.DEVNULL,
                            shell=True)
            print("Waiting for 3 sec")
            sleep(3)
            webbrowser.open_new_tab("http://localhost:8000/")
            self.sc.headers['User-Agent'] = self.sc.get("http://localhost:8000/get").text
            p.kill()
        except Exception as e:
            print("Failed fetching from browser ({})".format(e))
        return cookies, self.sc.headers['User-Agent']


    def fetch_chko(self, url, cookies):
        resp = self.sc.get(url, cookies=cookies)
        resp_lo_js = self.sc.get("https://kissmanga.com/Scripts/lo.js", cookies=cookies)
        parser = chko_parser()
        chko = []
        #lo.js
        lo_js = resp_lo_js.text.encode().decode('unicode-escape')
        blob = lo_js.split(';')
        for val in blob:
            if "chko=" in val:
                chko_index = val.split('[', 1)[1].split(']')[0]
                break
        l = blob[0].split('[', 1)[1].split(']')[0].split('"')[1::2]
        chko.append(l[int(chko_index)])
        #resp.html
        parser.feed(resp.text)
        chko.append(parser.chko)
        return ''.join(chko)

    def get_from_cloudscraper(self, url):
        print("Getting cookies & chko")
        try:
            _ = self.sc.get(url)
            __cfduid = self.sc.cookies.get('__cfduid', '', domain=".kissmanga.com")
            cf_clearance = self.sc.cookies.get('cf_clearance', '', domain=".kissmanga.com")
            cookies = "__cfduid={};cf_clearance={}".format(__cfduid, cf_clearance)
            user_agent = self.sc.headers['User-Agent']
        except Exception as e:
            print("Error : Unable to fetch data from site, try updating cloudscraper dependency with \"pip install -U cfscrape\".")
            print(e)
        return cookies, user_agent

def pass_all_to_fmd(path, cookies, agent, additional_cookies,chko, ignore_chko):
    print("Exporting cookies to FMD's settings")
    try:
        with open(path, 'r+') as f:
            data = json.load(f)
            for i in data:
                if i['Website'] == 'KissManga':
                    i['Settings']['HTTP']['Cookies'] = cookies if additional_cookies == "" else cookies + ";" + additional_cookies
                    i['Settings']['HTTP']['UserAgent'] = agent
                    if not ignore_chko:
                        i['Options']['Key'] = chko
                    break
            f.seek(0)
            json.dump(data, f, ensure_ascii=False)
            f.truncate()
    except:
        print("Error : Unable to open modules.json. Put this script in the same folder or specify it's path")

def main(path, refresh, random_time, add_cookie, url, ignore_chko, use_browser, browser_type):
    print("Creating session")
    s = Scraper()
    print("Updating KissManga's Cookies\n----------//----------")
    try:
        if use_browser:
            cookies, u_agent = s.get_from_browser(".kissmanga.com", browser_type)
        else:
            cookies, u_agent = s.get_from_cloudscraper(url)
        if not ignore_chko:
            chko = s.fetch_chko(url, cookies)
        pass_all_to_fmd(path, cookies, u_agent, add_cookie, chko, ignore_chko)
    except Exception as e:
        print("Error occured ({})".format(e))
    print("Finished!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', dest="path", help="Specify modules.json path")
    parser.set_defaults(path="modules.json")
    parser.add_argument('--refresh', dest="replace", help="Set default refresh time (in seconds)")
    parser.set_defaults(refresh=600)
    parser.add_argument('--randomizer', dest="randomizer", help="Set max value (in seconds) for refresh time randomizer (refresh time = refresh time + rand(0, value))")
    parser.set_defaults(randomizer=60)
    parser.add_argument('--a', dest="add_cookie", help="Add another cookies on top of cfuid and cf_clearance")
    parser.set_defaults(add_cookie="")
    parser.add_argument('--url', dest="url", help="Set url for kissmanga page")
    parser.set_defaults(url="https://kissmanga.com/Manga/4-Cut-Hero/Ch-000--Prologue")
    parser.add_argument('--ignore-chko', dest='ignore_chko', action='store_true', help="ignore fetching chko value")
    parser.set_defaults(ignore_chko=False)
    parser.add_argument('--use-browser', dest='use_browser', action='store_true', help="Use cookies and header from browser")
    parser.set_defaults(use_browser=True)
    parser.add_argument('--use-browser-type', dest='use_browser', action='store_true', help="Set default browser")
    parser.set_defaults(browser_type="firefox")
    args = parser.parse_args()

    main(args.path, args.refresh, args.randomizer, args.add_cookie, args.url, args.ignore_chko, args.use_browser, args.browser_type)
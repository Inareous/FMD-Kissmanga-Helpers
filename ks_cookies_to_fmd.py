import cloudscraper #https://github.com/VeNoMouS/cloudscraper
import json
import argparse
from html.parser import HTMLParser
import re
from helpers.selenium_utils import *

# class chko_parser(HTMLParser):
#     def __init__(self):
#         HTMLParser.__init__(self)
#         self.chko = ''

#     def handle_data(self, data):
#         if 'chko' in data:
#             s_hex = re.findall(r'\[(.*?)\]', data)[0].replace('\"','')
#             val = s_hex.encode().decode('unicode-escape')
#             self.chko += val

class Scraper:
    def __init__(self):
        self.sc = cloudscraper.create_scraper()

    # def fetch_chko(self, url, cookies, u_agent):
    #     self.sc.headers['User-Agent'] = u_agent
    #     resp = self.sc.get(url, cookies=cookies)
    #     resp_lo_js = self.sc.get("https://kissmanga.com/Scripts/lo.js", cookies=cookies)
    #     parser = chko_parser()
    #     chko = []
    #     #lo.js
    #     lo_js = resp_lo_js.text.encode().decode('unicode-escape')
    #     blob = lo_js.split(';')
    #     for val in blob:
    #         if "chko=" in val:
    #             chko_index = val.split('[', 1)[1].split(']')[0]
    #             break
    #     l = blob[0].split('[', 1)[1].split(']')[0].split('"')[1::2]
    #     chko.append(l[int(chko_index)])
    #     #resp.html
    #     parser.feed(resp.text)
    #     chko.append(parser.chko)
    #     return ''.join(chko)

    def get_from_cloudscraper(self, url, domain, keys):
        cookies = {}
        try:
            _ = self.sc.get(url)
            for key in keys:
                cookies[key] = self.sc.cookies.get(key, '', domain=domain)
            user_agent = self.sc.headers['User-Agent']
        except Exception as e:
            print("Error : Unable to fetch data from site, try updating cloudscraper dependency with \"pip install -U cfscrape\".")
            print(e)
        return cookies, user_agent

def pass_all_to_fmd(path, cookies, agent, additional_cookies):
    print("Exporting cookies to FMD's settings")
    cookie_string = ";".join([str(key)+"="+str(val) for key,val in cookies.items()])
    try:
        with open(path, 'r+') as f:
            data = json.load(f)
            for i in data:
                if i['ID'] == '4f40515fb43640ddb08eb61278fc97a5': #kissmanga
                    i['Cookies'] = [] #Wipe FMD2's weird cookiejar
                    i['Settings']['Enabled'] = True
                    i['Settings']['HTTP']['Cookies'] = cookie_string if additional_cookies == "" else cookie_string + ";" + additional_cookies
                    i['Settings']['HTTP']['UserAgent'] = agent
                    break
            f.seek(0)
            json.dump(data, f, ensure_ascii=False)
            f.truncate()
        print("Settings exported")
    except:
        print("Error : Unable to open modules.json. Put this script in the same folder or specify it's path")

def main(path, add_cookie, url, use_selenium):
    print("Creating session")
    s = Scraper()
    print("Updating KissManga's Cookies")
    cookies = {}
    u_agent = ""
    try:
        domain = ".kissmanga.com"
        keys = ['__cfduid','cf_clearance']
        if use_selenium:
            print("Fetching Cookies using selenium module")
            cookies, u_agent = SeleniumBrowser().open_link(url, domain, keys)
        else:
            print("Fetching Cookies using cloudscraper module")
            cookies, u_agent = s.get_from_cloudscraper(url, domain, keys)
        print("----------//----------")
        pass_all_to_fmd(path, cookies, u_agent, add_cookie)
    except Exception as e:
        print("Error occured ({})".format(e))
    print("Finished!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--path', dest="path", help="Specify modules.json path")
    parser.set_defaults(path="modules.json")
    parser.add_argument('--a', dest="add_cookie", help="Add another cookies on top of cfuid and cf_clearance")
    parser.set_defaults(add_cookie="")
    parser.add_argument('--url', dest="url", help="Set url for kissmanga page")
    parser.set_defaults(url="https://kissmanga.com/Manga/4-Cut-Hero/Ch-000--Prologue")
    parser.add_argument('--use-selenium', dest='use_selenium', action='store_true', help="Use selenium")
    parser.set_defaults(use_selenium=False)
    args = parser.parse_args()

    main(args.path, args.add_cookie, args.url, args.use_selenium)
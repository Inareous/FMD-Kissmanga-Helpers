import cloudscraper #https://github.com/VeNoMouS/cloudscraper
import re
from bs4 import BeautifulSoup
import sqlite3
import pickle
import httpx
import asyncio
import datetime
import colorama
import unicodedata
import browser_cookie3
import webbrowser
import argparse
import subprocess
import os
from time import sleep
from helpers import logger, browser_utils

class Scraper:
    def __init__(self, logger, args):
        self.sc = cloudscraper.create_scraper()
        self.BASE_URL = ''
        self.logger = logger
        self.args = args
    
    def create_connection(self, use_browser = True):
        self.logger.print("Establishing connection to server", 0)
        domain = ".kissmanga.com"
        keys = ['__cfduid','cf_clearance']
        cookies = {}
        ok = False
        try:
            _ = self.sc.get(self.BASE_URL)
            for key in keys:
                cookies[key] = self.sc.cookies.get(key, '', domain=domain)
            ok = True
        except Exception as e:
            if "reCaptcha" in e.args[0]:
                self.logger.print("reCaptcha detected, try using reCaptcha solver or fetch from browser", 1)
        if not ok and use_browser:
            self.logger.print("Fetching credentials from your browser", 0)
            cookies, u_agent = browser_utils.fetch_cred_from_browser(domain, keys)
        self.init_httpx(cookies, u_agent, domain, keys)

    def init_httpx(self, cookies, user_agent, domain, keys):
        self.logger.print("Initiating Httpx session with settings from Request", 0)
        headers = {'User-Agent' : user_agent}
        self.session = httpx.Client(cookies=cookies, headers=headers)

    def close(self):
        self.session.close()
        self.sc.close()

    def fetch_num_pages(self, url):
        #get cookies & headers from this
        self.logger.print("Fetching total number of pages",0)
        resp = self.session.get(url)
        soup = BeautifulSoup(resp.text, features="lxml")
        num = int(soup.find("ul", class_="pager").find_all("li")[-1].contents[0]['page'])
        return num

    def fetch_manga_info(self, manga_url):
        resp = self.session.get(manga_url)
        soup = BeautifulSoup(resp.text, features="lxml")
        bigBarContainer = soup.find("div", class_="bigBarContainer")
        p_tag = bigBarContainer.find_all("p")
        artist = ""
        for p in p_tag:
            if "Genre" in p.text:
                g_l = p.find_all("a")
                genre_list = []
                for val in g_l:
                    genre_list.append(val.text)
                genre = ", ".join(genre_list)
            if "Author" in p.text or "Writer" in p.text:
                author_tag = p.find_all("a")
                author_list = []
                if author_tag:
                    for val in author_tag:
                        author_list.append(val.text)
                    author = ", ".join(author_list)
                else:
                    author = "N/A"
            if "Status" in p.text:
                if "Completed" in p.text:
                        status = "1"
                else:
                    status = "0"
            if "Summary" in p.text:
                summ = []
                summ.append(p.text)
                sib = p.find_next_siblings()
                if sib:
                    for val in sib:
                        summ.append(val.text)
                summary = "".join(summ)
                summary = summary.replace("\nSummary:\n","")
                summary = unicodedata.normalize("NFKD", summary)
                break #last
        numchapter = len(soup.find("table", class_="listing").find_all("a"))
        jdn = "2458878" #fixed number following previous .db
        return {
            'authors' : author,
            'artists' : artist,
            'genres' : genre,
            'summary' : summary,
            'status'  : status,
            'numchapter' : numchapter,
            'jdn' : jdn,
        }

    def fetch_manga_per_page(self, page_url):
        data = []
        resp = self.session.get(page_url)
        soup = BeautifulSoup(resp.text, features="lxml")
        tr = soup.find("table", class_="listing").find_all("tr")
        for _, val in enumerate(tr):
            try:
                title = val.find("a").text
                title = title.replace("\n","")
                href = val.find("a")['href']
                data.append({'title': title, 'link':href})
            except:
                pass
        return data
    
    def rerun(self, data, err_bucket, max_retry, mode):
        counter = 0
        while len(err_bucket) > 0 and counter < 10:
            counter += 1
            err_length = len(err_bucket)
            for i in range(err_length):
                if mode == "fetch_manga_per_page":
                    try:
                        link = err_bucket.pop(0)
                        self.logger.print("Rerun - Fetching manga page [{:<5}/{:<5}] -- {}".format(i+1, err_length, link),0)
                        l = self.fetch_manga_per_page(link)
                        data.extend(l)
                    except:
                        self.logger.print("Error in fetching {} || Counter = {}/{}".format(link, counter, max_retry),1)
                        err_bucket.append(link)
                if mode == "fetch_manga_info":
                    try:
                        pop = err_bucket.pop(0)
                        self.logger.print("Rerun - Fetching manga info [{:<5}/{:<5}] -- {}".format(i+1, err_length, pop['link']),0)
                        info = self.fetch_manga_info(pop['link'])
                        data[pop['index']] = {'title':data[pop['index']]['title'], 'link':data[pop['index']]['link'], **info}
                    except:
                        self.logger.print("error in fetching {} || Counter = {}/{}".format(pop['link'], counter, max_retry),1)
                        err_bucket.append({'index' : pop['index'], 'link' : pop['link']})
        return data

    def run(self, BASE_URL):
        self.BASE_URL = BASE_URL
        self.create_connection()
        list_url = "{}/MangaList/Newest".format(self.BASE_URL)
        data = []
        err_bucket = []
        max_retry = 10
        end = self.fetch_num_pages(list_url)
        for i in range(1, end+1):
            try:
                self.logger.print("Fetching manga page -- {}?page={}".format(list_url, i),0)
                l = self.fetch_manga_per_page("{}?page={}".format(list_url, i))
                data.extend(l)
            except:
                self.logger.print("Error in fetching {}?page={} || Adding to backup error list for rerun".format(list_url, i),1)
                err_bucket.append("{}?page={}".format(list_url, i))
        if len(err_bucket) > 0:
            data = self.rerun(data, err_bucket, max_retry, "fetch_manga_per_page")
            err_bucket.clear()
        for idx, val in enumerate(data):
            try:
                self.logger.print("Fetching manga info [{:<5}/{:<5}] -- {}".format(idx, len(data), self.BASE_URL+val['link']),0)
                info = self.fetch_manga_info(self.BASE_URL+val['link'])
                data[idx] = {'title':val['title'], 'link':val['link'], **info}
            except:
                self.logger.print("Error in fetching {} || Adding to backup error list for rerun".format(self.BASE_URL+val['link']),1)
                err_bucket.append({'index' : idx, 'link' : self.BASE_URL+val['link']})
        if len(err_bucket) > 0:
            data = self.rerun(data, err_bucket, max_retry, "fetch_manga_info")
        data = sorted(data, key=lambda k: k['title']) 
        return data

class DB:
    def __init__(self, file):
        self.create_connection(file)

    def create_connection(self, db_file):
        self.conn = None
        try:
            self.conn = sqlite3.connect(db_file)
        except sqlite3.Error as e:
            print(e)
    
    def execute_query(self, query):
        try:
            c = self.conn.cursor()
            c.execute(query)
        except sqlite3.Error as e:
            print(e)

    def create_table_kissmanga(self):
        sql_create_table = """CREATE TABLE IF NOT EXISTS masterlist (
                                    link TEXT PRIMARY KEY,
                                    title TEXT NOT NULL,
                                    authors TEXT,
                                    artists TEXT,
                                    genres TEXT,
                                    status TEXT,
                                    summary TEXT,
                                    numchapter INTEGER,
                                    jdn INTEGER
                                );"""
        self.execute_query(sql_create_table)
    
    def post_row(self, tablename, rec):
        try:
            c = self.conn.cursor()
            keys = ','.join(rec.keys())
            question_marks = ','.join(list('?'*len(rec)))
            values = tuple(rec.values())
            c.execute('INSERT OR REPLACE INTO '+tablename+' ('+keys+') VALUES ('+question_marks+')', values)
        except Exception as e:
            print("Error : Exception in inserting data ({})".format(e))

    def insert_data_kissmanga(self, data):
        for _, manga in enumerate(data):
                self.post_row("masterlist", manga)

    def save_and_close(self):
        try:
            self.conn.commit()
            self.conn.close()
        except sqlite3.Error as e:
            print(e)

def main(args):
    print("-- Start --")
    logger_ = logger.Logger()
    sc = Scraper(logger_, args)
    data = sc.run("https://kissmanga.com")
    sc.close()
    # Pickling
    with open('pickle_data', 'wb') as fp:
        pickle.dump(data, fp)
    #temp save
    with open ('pickle_data', 'rb') as fp:
        data = pickle.load(fp)
    # eof pickling
    logger_.print("-- Finished scraping data, saving to .db --",0)
    db = DB("KissManga.db")
    db.create_table_kissmanga()
    db.insert_data_kissmanga(data)
    db.save_and_close()
    logger_.stop()
    print("-- Stop --")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--user-agent', dest="user_agent", help="Specify modules.json path")
    parser.set_defaults(user_agent="")
    parser.add_argument('--browser', dest="browser", help="Set default refresh time (in seconds)")
    parser.set_defaults(refresh="")
    parser.add_argument('--enable-browser', dest='enable_browser_cookies', action='store_true', help="ignore fetching chko value")
    parser.set_defaults(enable_browser_cookies=False)
    args = parser.parse_args()
    main(args)
import cloudscraper #https://github.com/VeNoMouS/cloudscraper
import re
from bs4 import BeautifulSoup
import sqlite3
import pickle
import httpx
import asyncio
import unicodedata
import argparse
import aiometer
from helpers import logger_utils, browser_utils, db_utils

class Scraper:
    def __init__(self, logger):
        self.sc = cloudscraper.create_scraper()
        self.BASE_URL = ''
        self.logger = logger

    def create_connection(self, use_browser):
        self.logger.checkpoint("Establishing connection to server")
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
                self.logger.error("reCaptcha detected, try using reCaptcha solver or fetch from browser")
        if not ok and use_browser:
            self.logger.info("Fetching credentials from your browser")
            cookies, u_agent = browser_utils.fetch_cred_from_browser(domain, keys)
        self.init_httpx(cookies, u_agent, domain, keys)

    def init_httpx(self, cookies, user_agent, domain, keys):
        self.logger.checkpoint("Initiating Httpx session with settings from Request")
        headers = {'User-Agent' : user_agent}
        httpx_cookies = httpx.Cookies()
        for key in keys:
            httpx_cookies.set(key, cookies[key], domain=domain)
        self.session = httpx.AsyncClient(headers=headers, cookies=httpx_cookies)

    async def close(self):
        await self.session.aclose()
        self.sc.close()

    async def fetch_num_pages(self, url):
        self.logger.checkpoint("Fetching total number of pages")
        resp = await self.session.get(url)
        soup = BeautifulSoup(resp.text, features="lxml")
        num = int(soup.find("ul", class_="pager").find_all("li")[-1].contents[0]['page'])
        return num

    async def fetch_manga_info(self, t):
        manga_url, index, end = t
        self.logger.info("Fetching manga info [{:<5}/{:<5}] -- {}".format(index, end, manga_url))
        status = 0
        try:
            resp = await self.session.get(manga_url)
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
                        manga_status = "1"
                    else:
                        manga_status = "0"
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
            result = {
                'authors' : author,
                'artists' : artist,
                'genres' : genre,
                'summary' : summary,
                'status'  : manga_status,
                'numchapter' : numchapter,
                'jdn' : jdn,
            }
        except:
            status = -1
            self.logger.error("Failed fetching {}".format(manga_url))
            return status, (manga_url, index)
        return status, (result, index)

    async def fetch_manga_per_page(self, t):
        page_url, index, end = t
        self.logger.info("Fetching manga page [{:<5}/{:<5}] -- {}".format(index, end, page_url))
        data = []
        status = 0 # 0 = Success, -1 = Fail
        try:
            resp = await self.session.get(page_url)
            soup = BeautifulSoup(resp.text, features="lxml")
            tr = soup.find("table", class_="listing").find_all("tr")
            for _, val in enumerate(tr):
                try:
                    title = val.find("a").text
                    title = bytes(title, 'utf-8').decode('utf-8', 'ignore')
                    title = " ".join(title.split())
                    href = val.find("a")['href']
                    data.append({'title': title, 'link':href})
                except:
                    pass
        except:
            status = -1
            self.logger.error("Failed fetching {}".format(page_url))
            return status, (page_url, index)
        return status, data

    async def fetch_async(self, func, requests, max_at_once, max_per_second):
        data = []
        err_bucket = []
        async with aiometer.amap(
            func,
            requests,
            max_at_once=max_at_once, # Limit maximum number of concurrently running tasks.
            max_per_second=max_per_second,  # Limit request rate to not overload the server.
        ) as results:
            async for status, resp in results:
                if status == 0:
                    data.append(resp)
                elif status == -1:
                    err_bucket.append(resp)
        err_bucket = [(x,y,len(err_bucket)) for x,y in err_bucket]
        return data, err_bucket

    async def run(self, BASE_URL, use_browser=False, max_at_once=20, max_per_second=10, max_retry=10):
        self.BASE_URL = BASE_URL
        list_url = "{}/MangaList/Newest".format(self.BASE_URL)
        data = []
        retry_counter = 0
        self.create_connection(use_browser)
        total_pages = await self.fetch_num_pages(list_url)
        requests = [("{}?page={}".format(list_url, index), index, total_pages) for index in range(1, total_pages+1)]
        self.logger.checkpoint("Fetching manga from {} pages".format(total_pages))
        results, err_bucket = await self.fetch_async(self.fetch_manga_per_page, requests, max_at_once, max_per_second)
        for result in results:
            data.extend(result)
        while len(err_bucket) > 0 and retry_counter < max_retry:
            retry_counter += 1
            self.logger.checkpoint("Re-run {} links. Retry attempt = [{}/{}]".format(len(err_bucket), retry_counter,max_retry))
            results, err_bucket = self.fetch_async(self.fetch_manga_per_page, err_bucket, max_at_once, max_per_second)
            for result in results:
                data.extend(result)
        retry_counter = 0
        self.logger.checkpoint("Finished getting manga list from {} pages. Total manga : {}".format(total_pages, len(data)))
        requests = [(self.BASE_URL+data[index]['link'], index, len(data)) for index in range(len(data))]
        self.logger.checkpoint("Fetching manga info (detail) for {} manga".format(len(data)))
        results, err_bucket = await self.fetch_async(self.fetch_manga_info, requests, max_at_once, max_per_second)
        for result, index in results:
            data[index].update(result)
        while len(err_bucket) > 0 and retry_counter < max_retry:
            retry_counter += 1
            self.logger.checkpoint("Re-run {} links. Retry attempt = [{}/{}]".format(len(err_bucket), retry_counter,max_retry))
            results, err_bucket = await self.fetch_async(self.fetch_manga_info, err_bucket, max_at_once, max_per_second)
            for result, index in results:
                data[index].update(result)
        if len(err_bucket) > 0:
            self.logger.warning("Link error list is not 0!")
        self.logger.checkpoint("Finished getting manga info. Sorting data")
        data = sorted(data, key=lambda k: k['title'])
        return data

async def main(args):
    print("-- Start --")
    logger = logger_utils.Logger()
    sc = Scraper(logger)
    data = await sc.run("https://kissmanga.com", use_browser=args.enable_browser_cookies)
    await sc.close()
    # Pickling
    logger.checkpoint("-- Saving data temporarily to pickle file --")
    with open('data.pickle', 'wb') as fp:
        pickle.dump(data, fp)
    # eof pickling
    logger.checkpoint("-- Finished scraping data, saving to .db --")
    db = db_utils.DB("KissManga.db")
    db.create_table_kissmanga()
    db.insert_data_bulk(tablename='masterlist', entries=data)
    db.save_and_close()
    logger.stop()
    print("-- Finished --")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--enable-browser', dest='enable_browser_cookies', action='store_true', help="Use creds from browser")
    parser.set_defaults(enable_browser_cookies=False)
    args = parser.parse_args()
    asyncio.run(main(args))
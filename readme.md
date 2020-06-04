A collection of simple script I use to make using [Free Manga Downloader](https://github.com/fmd-project-team/FMD) on kissmanga site easier.

# Dependencies
- Python 3.x
- **[aiometer](https://github.com/florimondmanca/aiometer)**
- **[browser_cookie3](https://github.com/borisbabic/browser_cookie3)**
- **[BeautifulSoup](https://pypi.org/project/beautifulsoup4/)** 
- **[cloudsraper](https://github.com/VeNoMouS/cloudscraper)** 
- **[colorama](https://github.com/tartley/colorama)** <sup>*(I like pretty colors, deal with it)*</sup>
- **[httpx](https://github.com/encode/httpx)** 

# What's in here

- `create_ks_database` is a script to create KissManga.db used in [Free Manga Downloader](https://github.com/fmd-project-team/FMD).
- `ks_cookies_to_fmd` is a script to update Kissmanga's cookies and user agent in FMD.
- `Run.bat` is a script i use to call `ks_cookies_to_fmd` and open FMD automatically.

# How do I use this

If you want to update your Kissmanga's FMD cookies, do the following:

1. Install Python and all dependencies listed
2. Download or copy this repo
3. Copy & Edit `Run_example.bat`
   
    Make sure you change `USE_BROWSER` to true or false.
    
    If you set `USE_BROWSER` to `true`, open your browser and make sure you can navigate kissmanga.com and not blocked by cloudflare, the script will fetch cookies from your browser. Setting it to `false` will set the script to use the [cloudsraper](https://github.com/VeNoMouS/cloudscraper) module to try bypassing clouflare protection.

    Leave `URL` empty unless you really need to for some reason, the default url used is `https://kissmanga.com/Manga/4-Cut-Hero/Ch-000--Prologue`

    `IGNORE_CHKO` is there if you want to ignore updating chko value in your FMD. IIRC IV is never updated but sometimes chko does.

4. Run `Run_example.bat`
   
5. Misc : If you want, use `Run_example.bat` everytime you want to open FMD to make sure you get fresh cookies.
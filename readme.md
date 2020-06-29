A collection of simple script I use to make using [Free Manga Downloader](https://github.com/fmd-project-team/FMD) on kissmanga site easier.

# Dependencies
- Python 3.x
- **[aiometer](https://github.com/florimondmanca/aiometer)**
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

1. Install [Python 3.x](https://www.python.org/downloads/)
2. Download or copy [this repo](https://github.com/Inareous/FMD-Kissmanga-Helpers/archive/master.zip)
3. Install all dependencies listed (run pip manually or `pip install -r 
requirements.txt`)
4. Make sure you check your version of chrome, *this script assume you have Google Chrome v83. If you have other version of google chrome download `chromedriver.exe` [here](https://chromedriver.chromium.org/downloads) and replace the one on `/assets` folder*. 
5. Copy & Edit `Run_example.bat`

    Change the necessary path (`PYTHON_PATH`, `SCRIPT_PATH`, and `FMD_PATH`)

    Make sure you change `USE_SELENIUM` to true or false.
    
    If you set `USE_SELENIUM` to `true`, script will try to open Google Chrome and wait until you finished solving the challenge.
    
    Setting it to `false` will set the script to use the [cloudsraper](https://github.com/VeNoMouS/cloudscraper) module to try bypassing clouflare protection. *__Currently this doesnt work due to AreYouHuman2 challenge so you should set `USE_SELENIUM` to true__*.

    Leave `URL` empty unless you really need to for some reason, the default url used is `https://kissmanga.com/Manga/4-Cut-Hero/Ch-000--Prologue`

    `IGNORE_CHKO` is there if you want to ignore updating chko value in your FMD. IIRC IV is never updated but sometimes chko does.

6. Run your copy of `Run_example.bat`
   
7. Misc : If you want, use your `Run_example.bat` everytime you want to open FMD to make sure you get fresh cookies. Don't forget to change the icon too!
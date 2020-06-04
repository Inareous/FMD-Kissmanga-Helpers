from winreg import HKEY_CURRENT_USER, OpenKey, QueryValueEx
import browser_cookie3
from http.server import BaseHTTPRequestHandler, HTTPServer
import threading
from urllib.request import urlopen
import webbrowser

class Handler(BaseHTTPRequestHandler):
    Event_dictionary_list = {}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        if self.path == '/set':
            self.Event_dictionary_list['User-Agent'] = self.headers['User-Agent']
            self._set_response()
            self.wfile.write("<p>User agent set to : {}</p><p>You can close this tab</p>"
                            .format(self.Event_dictionary_list['User-Agent']).encode('utf-8'))
        if self.path == '/agent':
            self._set_response()
            self.wfile.write(self.Event_dictionary_list['User-Agent'].encode('utf-8'))

    def log_message(self, format, *args):
        return

class Server():
    def __init__(self,port=8000, url='http://localhost', handler = Handler):
        self.port = port
        self.handler = handler
        self.thread = None
        self.httpd = None                
        self.run = False

    def start(self, ):
        self.run =  True
        server_address = ('', self.port)
        self.httpd = HTTPServer(server_address, self.handler)
        self.thread = threading.Thread(target = self._serve)
        self.thread.start()
    
    def _serve(self):        
        while self.run:
            self.httpd.handle_request()

    def stop(self):
        self.run = False
        self.httpd.server_close()

def get_browser_type():
    reg_path = r'Software\\Microsoft\\Windows\\Shell\\Associations\\UrlAssociations\\https\\UserChoice'
    with OpenKey(HKEY_CURRENT_USER, reg_path) as key:
        browser_id = QueryValueEx(key, 'ProgId')
        if 'chrome' in browser_id[0].lower():
            return 'chrome'
        elif 'firefox' in browser_id[0].lower():
            return 'firefox'
    return browser_id

def fetch_cred_from_browser(domain, keys):
    browser_type = get_browser_type()
    port = 8001
    s = Server(port)
    s.start()
    #
    try:
        webbrowser.get(browser_type).open("http://localhost:{}/set".format(port))
    except:
        webbrowser.get().open("http://localhost:{}/set".format(port))
    user_agent = urlopen("http://localhost:{}/agent".format(port)).read().decode('utf-8')
    #
    s.stop()
    cookies = {}
    if browser_type == "firefox":
        cookie_jar = browser_cookie3.firefox(domain_name=domain)
    elif browser_type == "chrome":
        cookie_jar = browser_cookie3.chrome(domain_name=domain)
    for key in keys:
        cookies[key] = cookie_jar._cookies[domain]["/"][key].value
    return cookies, user_agent
import colorama
import datetime

class Logger:
    def __init__(self):
        colorama.init()
        self.count = 0
        self.start_time = datetime.datetime.now()

    def error(self, query):
        self.count +=1
        p = "[{:<5}|| {}] {:<10}: {}".format(self.count, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Error", query)
        print(colorama.Fore.RED + p + colorama.Style.RESET_ALL)
    
    def warning(self, query):
        self.count +=1
        p = "[{:<5}|| {}] {:<10}: {}".format(self.count, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Warning", query) 
        print(colorama.Fore.YELLOW + p + colorama.Style.RESET_ALL)

    def info(self, query):
        self.count +=1
        print("[{:<5}|| {}] {:<10}: {}".format(self.count, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Info", query))

    def checkpoint(self, query):
        self.count +=1
        p = "[{:<5}|| {}] {:<10}: {}".format(self.count, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Checkpoint", query)
        print(colorama.Fore.GREEN + p + colorama.Style.RESET_ALL)

    def stop(self):
        self.stop_time = datetime.datetime.now()
        delta = self.stop_time - self.start_time
        self.checkpoint("Logging stopped")
        self.info("Time start : {}".format(self.start_time))
        self.info("Time stop : {}".format(self.stop_time))
        self.info("Time delta : {}".format(delta))
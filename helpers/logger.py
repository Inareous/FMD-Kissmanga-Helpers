import colorama
import datetime

class Logger:
    def __init__(self):
        colorama.init()
        self.count = 0
        self.start_time = datetime.datetime.now()

    def print(self, query, status):
        if status == 0: # Status
            print("[{:<5}|| {}] {:<8}: {}".format(self.count, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Status", query))
        elif status == 1: # Error flag
            print(
                colorama.Fore.RED +
                "[{:<5}|| {}] {:<8}: {}".format(self.count, datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S"), "Error", query) + 
                colorama.Style.RESET_ALL
                )
        self.count += 1

    def stop(self):
        self.stop_time = datetime.datetime.now()
        delta = self.stop_time - self.start_time
        self.print("Logging stopped",0)
        self.print("Time start : {}".format(self.start_time),0)
        self.print("Time stop : {}".format(self.stop_time),0)
        self.print("Time delta : {}".format(delta),0)
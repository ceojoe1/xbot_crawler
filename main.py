
import schedule
import datetime
import os

from classes.mongo import Mongo
from classes.crawler import Crawl
from classes.menu import Menu
class colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
def clearConsole():
    command = 'clear'
    os.system(command)

def log(message, color=colors.HEADER, showTimestamp=True):
    d = datetime.datetime.now()
    timestamp = '%s/%s/%s @ %s:%s:%s' % (d.month, d.day, d.year, d.hour, d.minute, d.second),
    if (showTimestamp):
        print(color + "%s | %s" % (timestamp, message) + colors.ENDC)
    else:
        print(color + "%s" % (message) + colors.ENDC)

if __name__ == "__main__":
    db = Mongo(log, colors)
    menu = Menu(db, log, colors, clearConsole)
    user = db.load()
    while(True):
        if (user):
            while(True):
                clearConsole()
                menu.main_menu()
                option = int(input('What would you like to do: '))
                if (option == 1):
                    clearConsole()
                    menu.listener_menu()
                elif (option == 2):
                    clearConsole()
                    menu.alerts_menu()
                elif (option == 3):
                    clearConsole()
                    menu.scanners_menu()
                elif (option == 99):
                    db.deleteAll()
                    exit()
                elif (option == 0):
                    clearConsole()
                    log("Good scalping! See you next time.", showTimestamp=False)
                    exit()
        else:
            log("Welcome to the xBot Crawler, before you can run the tool you will need to configure a few things first.", colors.HEADER, False)
            log("1. You will need to configure a gmail account which allows the uses of less secure applications, to be able send text notifications to your mobile device. Please refer to the README on how to do that.", colors.OKBLUE, False)
            email = input("What is your gmail?  ->  ")
            password = input("What is your email password?  ->  ")
            number = input("Enter the phone number followed by the @ symbol and phone carrier you'd like to receive alerts on: (IE. 505123456@verizon)")
            if (email and password and number):
                db.update({"email":email, "password": password, "numbers": [], "carrier": "", "listeners": [], "alerts": [], "scanners":[]})
                db.addNumber(number)
                user = db.load()

            

    # sms_recipients = [
    #     {
    #         "number": "",
    #         "carrier": "verizon"
    #     }, 
    #     # {
    #     #     "number": "",
    #     #     "carrier": "att"
    #     # }, 
    #     # {
    #     #     "number": "",
    #     #     "carrier": "att"
    #     # }
    # ]

    # # bbUrl = "https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p?skuId=6428324"
    # bbUrl = "https://www.bestbuy.com/site/samsung-g97t-series-49-class-1000r-curved-gaming-monitor-black/6425569.p?skuId=6425569"
    # bestbuy = Crawl(bbUrl, 'add-to-cart-button', "Best Buy", sms_recipients)
    # bestbuy.scan()

    # # gsUrl = "https://www.gamestop.com/products/microsoft-xbox-series-x/224744.html"
    # # gamestop = Crawl(gsUrl, 'add-to-cart', "Game Stop", sms_recipients)
    # # gamestop.scan()

    # schedule.every(60).minutes.do(bestbuy.scan)
    # # schedule.every(60).minutes.do(gamestop.scan)

    # while True:
    #     schedule.run_pending()
  



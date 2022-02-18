from email import message
# from typing import Match
# from requests.api import head
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  

from threading import Thread
import smtplib
from email.message import EmailMessage, Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import schedule
import datetime

import pymongo
import pandas as pd


options = Options()
# options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--no-default-browser-check')
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--disable-default-apps')
options.add_argument('--disable-javascript')

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

def log(message, color=colors.HEADER, showTimestamp=True):
    d = datetime.datetime.now()
    timestamp = '%s/%s/%s @ %s:%s:%s' % (d.month, d.day, d.year, d.hour, d.minute, d.second),
    if (showTimestamp):
        print(color + "%s | %s" % (timestamp, message) + colors.ENDC)
    else:
        print(color + "%s" % (message) + colors.ENDC)


class DB:
    def __init__(self):
        self.client = pymongo.MongoClient('mongodb://root:toor@localhost:27017')
        self.db = self.client['scanner']
        self.document = self.db['user']

    def update(self, item):
        if(self.load()):
            print("loaded sometihng")
        else:
            self.document.insert_one(item)
            log("New Scanner Object created.")
    def load(self):
        return self.document.find_one()
    def setNumber(self, number):
        parseNumbers = number.split('@')
        activeDoc = self.load()
        self.document.update_one({"email": activeDoc['email']}, {"$set": { "number": parseNumbers[0], "carrier": parseNumbers[1]}})
        
        log('Number and Carrier updated')
    def addListener(self, listener):
        activeDoc = self.load()
        updatedDoc = self.document.update_one({"email": activeDoc['email']}, {"$push": {"listeners":listener}})
        log("Created a new Listener.")
    def getAllListeners(self):
        activeDoc = self.load()
        return activeDoc['listeners']
    def deleteAll(self):
        count = self.document.delete_many({})
        log_info = '{} documents deleted.'.format(count.deleted_count)
        log(log_info ,color=colors.FAIL, showTimestamp=False)
class Crawl:
    def __init__(self, url, className, store, recipients):
        log("Initializing Crawler for (%s)" % (store))

        self.url = url
        self.className = className
        self.store = store
        self.alert = False
        self.message = "initialized scanner"
        self.updated = datetime.datetime.now()
        self.status = False
        self.recipients = recipients

    
    def scan(self):
        t = Thread(target=self.scanner)
        t.start()
        # t.join()
        # print("Scanning Complete")

    def scanner(self):
        log("Starting Scanner Thread")
        
        self.updated = datetime.datetime.now()
        self.driver = webdriver.Chrome('./chromedriver', options=options)
        self.driver.get(self.url)
        element = self.driver.find_element(By.CLASS_NAME, self.className)
        if (element):
            updatedStatus = element.get_attribute('innerHTML')
            if (updatedStatus != self.status):
                self.alert = True

            self.status = updatedStatus
            self.message = "X-Box at %s are currently %s" % (self.store, self.status)
        self.driver.close()
        
        log("Completed Scanning")

        self.notify()

    def notify(self):
        data = self.getOutput()
        message = """__ %s __
        \n-- Updated: %s
        \n-- Status: %s
        \n-- %s \n
        """ % (data["Store"], data["Updated"], data["Status"], data["Message"])
        email = Email(self.recipients)
        email.send(message)

        
    
    def getStatus(self):
        return self.status

    def getOutput(self):
        d = self.updated
        self.output = {
            "Updated": '%s/%s/%s @ %s:%s:%s' % (d.month, d.day, d.year, d.hour, d.minute, d.second),
            "Store": self.store,
            "Url": self.url,
            "Status": self.status,
            "Alert": self.alert,
            "Message": self.message
        }
        return self.output

class Email:
   def __init__(self, recipients):
       log("Initializing SMS Connection")
       self.recipients = recipients
       self.email = "dev.joe.chacon@gmail.com"
       self.password = "Jmm12373618.."
    #    self.sms_gateway = "5057107534@mms.att.net"
       self.sms_gateways =  self.getGateways() #["5057107534@mms.att.net", "5056815786@vtext.com"]
       self.smtp = "smtp.gmail.com"
       self.port = 587
        
       self.server = smtplib.SMTP(self.smtp, self.port)
   def setEmail(self, email):
       self.email = email

   def setPassword(self, password):
       self.password = password

   def getGateways(self):
       gateways = []
       if (self.recipients and len(self.recipients) > 0):
           for r in self.recipients:
               if (r["carrier"] == "verizon"):
                   gateways.append(r["number"]+"@vtext.com")
               elif (r["carrier"] == "att"):
                   gateways.append(r["number"]+"@mms.att.net")
               elif (r["carrier"] == "tmobile"):
                   gateways.append(r["number"]+"@tmomail.net")
        
       return gateways

   def send(self, message):
       t = Thread(target=self.sender, args=(message,))
       t.start()
       
   def sender(self, message):
      log("Sending SMS notification")

      self.server.starttls()
      self.server.login(self.email, self.password)

      self.msg = MIMEMultipart()
      self.msg['From'] = self.email
      self.msg['To'] = ", ".join(self.sms_gateways)
      self.msg.attach(MIMEText(message, 'plain'))

      sms = self.msg.as_string()
      self.server.sendmail(self.email, self.sms_gateways, sms)
      self.server.quit()
    
      log("SMS Notification Sent")

class Menu:
        
    def main_menu(self):
        menu_options = {
            1: 'Listeners',
            2: 'Alerts',
            0: 'Exit',
            99: 'Delete Data'
        }
        log("----------------------------",color=colors.OKCYAN, showTimestamp=False)
        for key in menu_options.keys():
            option_print = '{} -- {}'.format(key, menu_options[key])
            log(option_print, color=colors.OKCYAN, showTimestamp=False)
        log("----------------------------",color=colors.OKCYAN, showTimestamp=False)
    def listener_menu(self, db):
        
        option = -1
        while(option != 0):
            listenerSize = len(db.getAllListeners())
            menu_options = {
                1: 'View All Listeners ({} active listeners)'.format(listenerSize),
                2: 'Add New Listener',
                3: 'Update Listener',
                4: 'Delete Listener',
                0: 'Main Menu'
            }
            log("----------------------------",color=colors.OKCYAN, showTimestamp=False)
            for key in menu_options.keys():
                option_print = '{} -- {}'.format(key, menu_options[key])
                log(option_print, color=colors.OKCYAN, showTimestamp=False)
            log("----------------------------",color=colors.OKCYAN, showTimestamp=False)

            option = int(input('choose an item: '))


            if (option == 1):
                listeners = db.getAllListeners()
                dfListeners = pd.DataFrame(listeners)
                print(dfListeners)
            elif (option == 2):
                log("In order to activate a listener you will need the URL of the website you would like me to watch as well as the CSS class name of the item you'd like me to monitor for change. Example:", color=colors.HEADER, showTimestamp=False)
                log("url: https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p?skuId=6428324, class-name: 'add-to-cart-button'", color=colors.BOLD, showTimestamp=False)
                company = input("Company: ")
                url = input("URL: ")
                className = input("Class-Name: ")
                listener = {
                    "company": company,
                    "url": url,
                    "className": className,
                }
                db.addListener(listener)
            elif(option == 3):
                listeners = db.getAllListeners()
                count = 1
                for listener in listeners:
                    option_print = '{} -- {}'.format(count, listener)
                    log(option_print, color=colors.BOLD, showTimestamp=False)
                    count = count + 1
        

if __name__ == "__main__":
    db = DB()
    # db.deleteAll()
    user = db.load()
    menu = Menu()
    while(True):
        if (user):
            while(True):
                menu.main_menu()
                option = int(input('What would you like to do: '))
                if (option == 1):
                    menu.listener_menu(db)
                elif (option == 99):
                    db.deleteAll()
                    exit()
                elif (option == 0):
                    log("Good scalping! See you next time.", showTimestamp=False)
                    exit()
        else:
            log("Welcome to the xBot Crawler, before you can run the tool you will need to configure a few things first.", colors.HEADER, False)
            log("1. You will need to configure a gmail account which allows the uses of less secure applications, to be able send text notifications to your mobile device. Please refer to the README on how to do that.", colors.OKBLUE, False)
            email = input("What is your gmail?  ->  ")
            password = input("What is your email password?  ->  ")
            number = input("Enter the phone number followed by the @ symbol and phone carrier you'd like to receive alerts on: (IE. 505123456@verizon)")
            if (email and password and number):
                db.update({"email":email, "password": password, "number": "", "carrier": "", "listeners": []})
                db.setNumber(number)
                user = db.load()

            

    # sms_recipients = [
    #     {
    #         "number": "5056815786",
    #         "carrier": "verizon"
    #     }, 
    #     # {
    #     #     "number": "5057150015",
    #     #     "carrier": "att"
    #     # }, 
    #     # {
    #     #     "number": "5057107534",
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
  



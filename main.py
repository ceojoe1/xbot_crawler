from email import message
from typing import Match
from requests.api import head
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

options = Options()
# options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--no-default-browser-check')
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--disable-default-apps')
options.add_argument('--disable-javascript')

def log(message):
    d = datetime.datetime.now()
    timestamp = '%s/%s/%s @ %s:%s:%s' % (d.month, d.day, d.year, d.hour, d.minute, d.second),
    print("%s | %s" % (timestamp, message))

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


if __name__ == "__main__":
    
    sms_recipients = [
        {
            "number": "5056815786",
            "carrier": "verizon"
        }, 
        {
            "number": "5057150015",
            "carrier": "att"
        }, 
        {
            "number": "5057107534",
            "carrier": "att"
        }
    ]

    bbUrl = "https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p?skuId=6428324"
    bestbuy = Crawl(bbUrl, 'add-to-cart-button', "Best Buy", sms_recipients)
    bestbuy.scan()

    gsUrl = "https://www.gamestop.com/products/microsoft-xbox-series-x/224744.html"
    gamestop = Crawl(gsUrl, 'add-to-cart', "Game Stop", sms_recipients)
    gamestop.scan()

    schedule.every(60).minutes.do(bestbuy.scan)
    schedule.every(60).minutes.do(gamestop.scan)

    while True:
        schedule.run_pending()
  



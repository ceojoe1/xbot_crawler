from threading import Thread
import datetime

from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options  

from .notification import Email

options = Options()
# options.add_argument("--headless")
options.add_argument('--no-sandbox')
options.add_argument('--no-default-browser-check')
options.add_argument('--disable-gpu')
options.add_argument('--disable-extensions')
options.add_argument('--disable-default-apps')
options.add_argument('--disable-javascript')

class Crawl:
    def __init__(self, db, log, colors):
        self.log = log
        self.db = db
        self.colors = colors
        self.alert = False
        self.message = "initialized scanner"
        self.updated = datetime.datetime.now()
        self.status = False

    def set(self,url='', className='', store='', recipients=[]):
        self.url = url
        self.className = className
        self.store = store
        self.recipients = recipients
    
    def scan(self):
        t = Thread(target=self.scanner)
        t.daemon = True
        t.start()
    
    def scanner(self):
        self.log("Starting Scanner")
        self.updated = datetime.datetime.now()
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        self.driver.get(self.url)

        element = self.driver.find_element(By.CLASS_NAME, self.className)

        if (element):
            updatedStatus = element.get_attribute('innerHTML')
            if (updatedStatus != self.status):
                self.alert = True

            self.status = updatedStatus
            self.message = "X-Box at %s are currently %s" % (self.store, self.status)
        self.driver.close()
        self.log("Completed scanning")
        self.notify()

    def notify(self):
        data = self.getOutput()
        message = """__ %s __
        \n-- Updated: %s
        \n-- Status: %s
        \n-- %s \n
        """ % (data["Store"], data["Updated"], data["Status"], data["Message"])
        programEmail = self.db.get('email')
        programPassword = self.db.get('password')
        email = Email(self.db, self.log, self.colors)
        email.set(email=programEmail, password=programPassword, recipients=self.recipients)
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
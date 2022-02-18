from email import message
import smtplib
from email.message import EmailMessage, Message
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from threading import Thread

class Email:
   def __init__(self, db, log, colors):
       log("Initializing SMS Connection")
       self.log = log
       self.db = db
       self.colors = colors
       self.smtp = "smtp.gmail.com"
       self.port = 587
       self.email = None
       self.password = None
       self.recipients = []
       self.sms_gateways = []
       self.server = smtplib.SMTP(self.smtp, self.port)
    
   def set(self, email='', password='', recipients=[]):
        self.email = email
        self.password = password
        self.recipients = recipients
        self.sms_gateways = self.getGateways()

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
       t.daemon = True
       t.start()
       
   def sender(self, message):
       for recipient in self.recipients:
        self.log("Sending SMS notification to: {}".format(recipient["number"]))

        self.server.starttls()
        self.server.login(self.email, self.password)

        self.msg = MIMEMultipart()
        self.msg['From'] = self.email
        self.msg['To'] = ", ".join(self.sms_gateways)
        self.msg.attach(MIMEText(message, 'plain'))

        sms = self.msg.as_string()
        self.server.sendmail(self.email, self.sms_gateways, sms)
        self.server.quit()
        
        self.log("SMS Notification Sent")
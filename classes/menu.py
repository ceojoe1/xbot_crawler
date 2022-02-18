import pandas as pd
import datetime

from .crawler import Crawl
class Menu:
    def __init__(self, db, log, colors, clearConsole):
        self.db = db
        self.log = log
        self.colors = colors
        self.clearConsole = clearConsole
    def main_menu(self):
        allListeners = self.db.get("listeners")
        allAlerts = self.db.get("alerts")
        allScanners = self.db.get("scanners")
        menu_options = {
            1: 'Listeners ({} active)'.format(len(allListeners)),
            2: 'Alerts ({}) active'.format(len(allAlerts)),
        }
        if (len(allListeners) > 0 and len(allAlerts) > 0):
            menu_options[3] = 'Scanner ({} available)'.format(len(allScanners)) 
        
        menu_options[0] = 'Exit'
        menu_options[99] =  'Delete Data'

        self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
        for key in menu_options.keys():
            option_print = '{} -- {}'.format(key, menu_options[key])
            self.log(option_print, color=self.colors.OKCYAN, showTimestamp=False)
        self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
    def listener_menu(self):
        option = -1
        while(option != 0):
            listeners = self.db.get("listeners")
            listenerSize = len(listeners)
            menu_options = {
                1: 'View All Listeners ({} active listeners)'.format(listenerSize),
                2: 'Add New Listener',
                3: 'Update Listener',
                4: 'Delete Listener',
                0: 'Main Menu'
            }
            self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
            for key in menu_options.keys():
                option_print = '{} -- {}'.format(key, menu_options[key])
                self.log(option_print, color=self.colors.OKCYAN, showTimestamp=False)
            self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)

            option = int(input('choose an item: '))
            if (option == 1):
                self.clearConsole()
                dfListeners = pd.DataFrame(listeners)
                self.log(dfListeners, showTimestamp=False)
            elif (option == 2):
                self.clearConsole()
                self.log("In order to activate a listener you will need the URL of the website you would like me to watch as well as the CSS class name of the item you'd like me to monitor for change. Example:", color=self.colors.HEADER, showTimestamp=False)
                self.log("url: https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p?skuId=6428324, class-name: 'add-to-cart-button'", color=self.colors.BOLD, showTimestamp=False)
                listenerName = input("Listener Name: ")
                company = input("Company: ")
                url = input("URL: ")
                className = input("Class-Name: ")
                listener = {
                    "name": listenerName,
                    "company": company,
                    "url": url,
                    "className": className,
                }
                self.db.addListener(listener)
            elif(option == 3):
                self.clearConsole()
                count = 1
                menu_options = {}
                for listener in listeners:
                    option_print = '{} -- {}'.format(count, listener)
                    self.log(option_print, color=self.colors.BOLD, showTimestamp=False)
                    count = count + 1
                option = int(input('choose a listener to update: '))
                listenerToUpdate = listeners[option -1]

                count = 1
                keys = listenerToUpdate.keys()

                self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
                for key in keys:
                    listeners[option-1][key] = input("{} = {} -> (Hit Enter to leave default, or enter a value) : ".format(key, listenerToUpdate[key])) or listenerToUpdate[key]
                 
                self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
                self.db.updateListeners(listeners)
            elif(option == 4):
                self.clearConsole()
                count = 1
                menu_options = {}
                for listener in listeners:
                    option_print = '{} -- {}'.format(count, listener)
                    self.log(option_print, color=self.colors.BOLD, showTimestamp=False)
                    count = count + 1
                option = int(input('choose a listener to delete: '))
                listeners.pop(option-1)
                self.db.updateListeners(listeners)
    def alerts_menu(self):
        option = -1
        allListeners = self.db.get('listeners') #self.db.getAllListeners()
        while(option != 0):
            alerts = self.db.get('alerts')
            alertsSize = len(alerts)
            menu_options = {
                1: 'View Active Alert ({} active alerts)'.format(alertsSize),
                2: 'Set Alert',
                3: 'Update Alert',
                4: 'Delete Alert',
                0: 'Main Menue'
            }
            self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
            for key in menu_options.keys():
                option_print = '{} -- {}'.format(key, menu_options[key])
                self.log(option_print, color=self.colors.OKCYAN, showTimestamp=False)
            self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)

            option = int(input('choose an item: '))
            if (option == 1):
                self.clearConsole()
                dfListeners = pd.DataFrame(alerts)
                self.log(dfListeners, showTimestamp=False)
            elif(option == 2):
                self.clearConsole()
                self.log('setting alert', showTimestamp=False)
                timeScale = input("At what interval would you like to scan? (day, hour, min, sec): ")
                frequency = int(input("How often would you like to scan? (1, 5, 60, 100): "))
                count = 1
                self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
                for listener in allListeners:
                    option_print = '{} -- {}'.format(count, listener["name"])
                    self.log(option_print, color=self.colors.OKCYAN, showTimestamp=False)
                    count = count + 1
                self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
                option = int(input("Which company do you want to attach the listener to? "))
                self.db.addAlert({"timeScale": timeScale, "frequency": frequency, "listener":allListeners[option -1]["name"]})
            elif(option == 3):
                self.clearConsole()
                count = 1
                menu_options = {}
                for alert in alerts:
                    option_print = '{} -- {}'.format(count, alert)
                    self.log(option_print, color=self.colors.BOLD, showTimestamp=False)
                    count = count + 1
                option = int(input('choose an alert to update: '))
                alertToUpdate = alerts[option -1]

                count = 1
                keys = alertToUpdate.keys()

                self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
                for key in keys:
                    alerts[option-1][key] = input("{} = {} -> (Hit Enter to leave default, or enter a value) : ".format(key, alertToUpdate[key])) or alertToUpdate[key]
                 
                self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
                self.db.updateAlerts(alerts)
            elif( option == 4):
                self.clearConsole()
                count = 1
                menu_options = {}
                for alert in alerts:
                    option_print = '{} -- {}'.format(count, alert)
                    self.log(option_print, color=self.colors.BOLD, showTimestamp=False)
                    count = count + 1
                option = int(input('choose an alert to delete: '))
                if(len(alerts) > 1):
                    alert.pop(option-1)
                    self.db.updateAlerts(alert)

                else:
                    self.db.updateAlerts([])
    def scanners_menu(self):
        option = -1
        while(option != 0):
            allScanners = self.db.get('scanners')
            listeners = self.db.get("listeners")
            menu_options = {
                1: 'View All Scanners ({} availalbe)'.format(len(allScanners)),
                2: 'Start Scanner',
                3: 'Edit Scanner',
                4: 'Delete Scanner',
                0: 'Main Menu'
            }
            self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
            for key in menu_options.keys():
                option_print = '{} -- {}'.format(key, menu_options[key])
                self.log(option_print, color=self.colors.OKCYAN, showTimestamp=False)
            self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)

            option = int(input('choose an item: '))
            if (option == 1):
                self.clearConsole()
                dfScanners = pd.DataFrame(allScanners)
                self.log(dfScanners, showTimestamp=False)
            elif (option == 2):
                self.clearConsole()
                count = 1
                self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
                for listener in listeners:
                    option_print = '{} -- {}'.format(count, listener['name'])
                    self.log(option_print, color=self.colors.OKCYAN, showTimestamp=False)
                    count = count + 1
                self.log("----------------------------",color=self.colors.OKCYAN, showTimestamp=False)
                option = int(input('Which Scanner would you like to start? '))
                activeScanner = listeners[option -1]
                activeScanner['active'] = True
                activeScanner['runtime'] = datetime.datetime.now()
                print(activeScanner)
                numbers = self.db.get('numbers')
                self.db.addScanner(activeScanner)
                crawler = Crawl(self.db, self.log, self.colors)
                crawler.set(url=activeScanner['url'], className=activeScanner['className'], store=activeScanner['name'], recipients=numbers)
                crawler.scan()
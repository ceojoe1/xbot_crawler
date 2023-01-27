import pymongo


class Mongo:
    def __init__(self, log, colors):
        self.log = log
        self.colors = colors
        self.client = pymongo.MongoClient('mongodb://MY_MONGO_INSTANCE')
        self.db = self.client['scanner']
        self.document = self.db['user']

    def update(self, item):
        if(self.load()):
            self.log("loaded database")
        else:
            self.document.insert_one(item)
            self.log("New Scanner Object created.")

    def updateListeners(self, data):
        activeDoc = self.load()
        oldListeners = activeDoc['listeners']        
        self.document.update_one({"email": activeDoc['email']}, {"$set": {"listeners": data}})
        print_log = "Updated listeners: {} -> {}".format(oldListeners, data)
        self.log(print_log)

    def updateAlerts(self, data):
        activeDoc = self.load()
        oldAlert = activeDoc['alerts']        
        self.document.update_one({"email": activeDoc['email']}, {"$set": {"alerts": data}})
        print_log = "Updated listeners: {} -> {}".format(oldAlert, data)
        self.log(print_log)
    
    def load(self):
        return self.document.find_one()

    def addNumber(self, number):
        parseNumbers = number.split('@')
        activeDoc = self.load()
        self.document.update_one({"email": activeDoc['email']}, {"$push": {"numbers": { "number": parseNumbers[0], "carrier": parseNumbers[1]}}})
        self.log('Number and Carrier updated')

    def addListener(self, listener):
        activeDoc = self.load()
        updatedDoc = self.document.update_one({"email": activeDoc['email']}, {"$push": {"listeners":listener}})
        self.log(updatedDoc)

    def addAlert(self, alert):
        activeDoc = self.load()
        self.document.update_one({"email": activeDoc['email']}, {"$push": {"alerts": alert}})
        self.log("Created a new Alert.")
    def addScanner(self, scanner):
        activeDoc = self.load()
        self.document.update_one({"email": activeDoc['email']}, {"$push": {"scanners": scanner}})
        self.log("Created a new Alert.")

    def get(self, item):
        activeDoc = self.load()
        # self.log("Loaded -> {} : {}".format(item, activeDoc[item]))
        return activeDoc[item]
    def deleteAll(self):
       count = self.document.delete_many({})
       log_info = '{} documents deleted.'.format(count.deleted_count)
       self.log(log_info ,color=self.colors.FAIL, showTimestamp=False)

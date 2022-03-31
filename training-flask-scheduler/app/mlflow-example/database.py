import pymongo

class DB:
    def __init__(self,host,port,username,password):
        self.myclient = pymongo.MongoClient("mongodb://{}:{}/".format(host,port),username=username,password=password)
        self.mydb = self.myclient["DUMMY"]
        self.dummy_col = self.mydb["dummy_col_demo"]
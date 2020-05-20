import pandas as pd
import numpy as np
import pymongo
from random import choices, sample
# connect to mongodb
MONGODB_DIR = "mongodb://<ip>:<port>"
recommend_db = pymongo.MongoClient(MONGODB_DIR)['Recommend']
# collections
user_product_event = recommend_db['user_product_events']
transactions = recommend_db['user_transactions']
user_recommend = recommend_db['user_recommends']
products = recommend_db['products']
categories = recommend_db['categories']
association_rules = recommend_db['association_rules']
# find data

class FindData():
    @staticmethod
    def find_user_transactions(transactions, user_id):
        try:
            trans = [p for p in transactions.find_one({'user_id':user_id})['trans']]  
            return trans
        except:
            return []
    @staticmethod
    def find_user_transactions(transactions, user_id):
        try:
            trans = [p for p in transactions.find_one({'user_id':user_id})['trans']]  
            return trans
        except:
            return []
class UpLoadData():
    @staticmethod
    def upload_data():
        pass

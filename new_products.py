#import library

#___________________________________________________
#import module
from connect_mongodb import *
from recommendation_system import RecommendationSys, utils
#___________________________________________________
#statics variable
#code

class NewProducts(RecommendationSys):
    def __init__(self):
        super().__init__()
    @staticmethod
    def update_new_item_list():
        NEW_ITEM_LIST = [i['product_id'] for i in products.find({'new': True}, {"product_id":1})]
        return NEW_ITEM_LIST
    @staticmethod
    def gennerate_recommend(NEW_ITEM_LIST, user_trans = []):
        NRP = 2
        n = len(user_trans) + NRP
        m = len(NEW_ITEM_LIST)
        if(m == 0): return []
        elif(n>m):
            return utils.diff(NEW_ITEM_LIST, user_trans)
        else:
            temp = sample(NEW_ITEM_LIST, k = m)
            return utils.diff(temp, user_trans)

if __name__ == "__main__":
    print("New products:", NewProducts.gennerate_recommend())






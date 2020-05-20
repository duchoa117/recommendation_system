#import library
import re
from random import sample
#___________________________________________________
#import module
from connect_mongodb import *
from recommendation_system import RecommendationSys, utils
#___________________________________________________
#static variable
#code

class TopProducts(RecommendationSys):
    def __int__(self):
        return super().__int__()
    @staticmethod
    def update_top_product():
        TOP_PRODUCT = [id['product_id'] for id in products.find({'new': False}).sort('rank', -1).limit(40)]
        return TOP_PRODUCT
    @staticmethod
    def gennerate_recommend(TOP_PRODUCT, user_trans = []):
        NRP = 6
        n = len(user_trans) + NRP
        top_n = utils.diff(TOP_PRODUCT, user_trans)
        if(len(top_n)>NRP):
            return sample(top_n, k = NRP)
        else:
            return sample(TOP_PRODUCT, k = NRP)
if __name__ == "__main__":
    print("Top products:", TopProducts.gennerate_recommend())










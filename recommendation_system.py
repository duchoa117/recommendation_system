#import library

#___________________________________________________
#import module
from connect_mongodb import *
import utils
#___________________________________________________
#code
class RecommendationSys():
    def __int__(self):
        pass
    @staticmethod
    def gennerate_recommend():
        pass
    @staticmethod
    def add_to_recommend_list(rs_list, products, pos, no):
        products = utils.diff(products, rs_list)
        n = len(products)
        for i in range(min(n, min(no, len(rs_list)-pos))):
            rs_list[pos+i] = products[i]
        return rs_list
    @staticmethod
    def update():
        pass
if __name__ == "__main__":
    print(RecommendationSys.add_to_recommend_list([1,2,3,4,5,6], [], 4, 10))



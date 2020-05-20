#import library
import time
from collections import defaultdict
from tqdm import trange
import datetime
from datetime import datetime
from itertools import combinations
import schedule 
#___________________________________________________
#import module
from connect_mongodb import *
from recommendation_system import RecommendationSys, utils
from association_rules import AssociationRules
from collaborative import CF
from content_based import ContentBased
from top_products import TopProducts
from new_products import NewProducts
#___________________________________________________
#static variables
RECOMMEND_FOR_NEW_USER = []
TOP_PRODUCT = []
NEW_ITEM_LIST = []
collaborative_model = CF()
association_model = AssociationRules()
#___________________________________________________
#code
def update_recommend_new_user():
    global RECOMMEND_FOR_NEW_USER
    global NEW_ITEM_LIST
    global TOP_PRODUCT
    global collaborative_model
    global association_model
    RECOMMEND_FOR_NEW_USER = TopProducts.gennerate_recommend(TOP_PRODUCT)
    new_products = NewProducts.gennerate_recommend(NEW_ITEM_LIST)
    RECOMMEND_FOR_NEW_USER = RecommendationSys.add_to_recommend_list(RECOMMEND_FOR_NEW_USER,new_products,5, 1)
    user_recommend.update_one({"user_id":"NEW_USER"}, {"$set":{"products":RECOMMEND_FOR_NEW_USER}}, upsert=True)
    # return RECOMMEND_FOR_NEW_USER
def get_action_make_recommend():
    global collaborative_model
    global association_model
    recommend_list = [] 
#     recommend list has 6 elements
    # print("start at", datetime.now().strftime("%H:%M:%S"))
    actions = user_product_event.find()
    for action in actions:
#         take information of this action
        user = action.get('user_id')
        product = action.get('product_id')
        event = action.get('event')
#       ________________________________
        try:
            user_trans_dict = transactions.find_one({'user_id':user})['trans']
            user_trans = [p for p in user_trans_dict]  # find user transactions
            user_trans_dict[product] = event
        except:
            user_trans_dict = {product:event}
            user_trans = []
        user_trans.append(product)
#       _______________________________
        try:
            recommend_list = TopProducts.gennerate_recommend(TOP_PRODUCT, user_trans)
            new_products = NewProducts.gennerate_recommend(NEW_ITEM_LIST, user_trans)
            recommend_list = RecommendationSys.add_to_recommend_list(recommend_list, new_products, 5, 1)
            content_based_re = ContentBased.gennerate_recommend(product, user_trans)
            recommend_list = RecommendationSys.add_to_recommend_list(recommend_list, content_based_re, 1, 2)
            collaborative_model.online_learning(user, product, event)
            collaborative_re = collaborative_model.genarate_recommend(user, user_trans)
            recommend_list = RecommendationSys.add_to_recommend_list(recommend_list, collaborative_re, 3, 2)
            association_re = association_model.gennerate_recommend(product, user_trans)
            recommend_list = RecommendationSys.add_to_recommend_list(recommend_list, association_re, 0, 1)
    #       update user(total+=1), user_recommend, update product(rank+=1)
            user_recommend.update_one({"user_id":user}, {"$set":{"products":recommend_list}}, upsert=True)
            transactions.update_one({"user_id":user}, {"$set":{"trans":user_trans_dict}, "$inc":{"total":1}}, upsert=True)
            products.update_one({"product_id":product}, {"$inc":{"rank":1}})
            user_product_event.delete_one({"user_id":user, "product_id":product})
        except Exception as e:
            print(e)
            print("BUG AT", datetime.now().strftime("%H:%M:%S"),"user:", user ,"product_id:", product)
            user_product_event.delete_one({"user_id":user, "product_id":product})
            continue
    # print("end at", datetime.now().strftime("%H:%M:%S"))
def job_shedule():
    global RECOMMEND_FOR_NEW_USER
    global NEW_ITEM_LIST
    global TOP_PRODUCT
    global collaborative_model
    global association_model
    RECOMMEND_FOR_NEW_USER = update_recommend_new_user()
    NEW_ITEM_LIST = NewProducts.update_new_item_list()
    TOP_PRODUCT = TopProducts.update_top_product()
    ContentBased.cold_start()
    association_model.cold_start()
def main():
    #0. global variable
    global RECOMMEND_FOR_NEW_USER
    global NEW_ITEM_LIST
    global TOP_PRODUCT
    global collaborative_model
    global association_model
    # cold start:
    #1. Content Based:
    print("COLD START CONTENT BASED")
    ContentBased.cold_start()
    #2. Collaborative:
    print("COLD START COLLABORATIVE")
    collaborative_model.cold_start()
    #3. Association:
    print("COLD START ASSOCIATION")
    association_model.cold_start()
    #4. NEW_ITEM, ITEM_FOR_NEW_USER
    NEW_ITEM_LIST = NewProducts.update_new_item_list()
    TOP_PRODUCT = TopProducts.update_top_product()
    RECOMMEND_FOR_NEW_USER = update_recommend_new_user()
    #5. schedule
    schedule.every().day.at("02:00").do(job_shedule)
    # CODE #
    while(1):
        # update_for_new_user every 3 A.M
        schedule.run_pending()
        get_action_make_recommend()
if __name__ == "__main__":
    main()
    

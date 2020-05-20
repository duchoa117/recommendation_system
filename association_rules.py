#import library
import time
from collections import defaultdict
from tqdm import trange
import datetime
from itertools import combinations
#___________________________________________________
#import module
from connect_mongodb import *
from recommendation_system import RecommendationSys, utils
#___________________________________________________
#static variables

#___________________________________________________

#code

class AssociationRules(RecommendationSys):
    def __init__(self, min_sup=0.006, min_conf=0.5):
        self.min_sup = min_sup
        self.min_conf = min_conf
        self.transactions = None
        self.rules = None
    def generate_transactions(self):
        print("Pull data....")
        self.transactions = defaultdict(list) 
        self.N = 0 #number of trans
        for i in transactions.find({}, {'trans'}):
            self.transactions[self.N] = list(i['trans'].keys())
            self.N += 1
    def calculate_itemsets_one(self):
        print("Calculate itemsets with one procuct...")
        temp = defaultdict(int)
        one_itemsets = dict()
        for key, items in self.transactions.items():
            for item in items:
                inx = frozenset({item})
                temp[inx] += 1
        # remove all items that is not supported.
        for key, itemset in temp.items():
            if itemset > self.min_sup * self.N:
                one_itemsets[key] = itemset
        return one_itemsets
    def has_support(self, items, one_itemsets):
        count = 0
        for item in one_itemsets:
            for i in items:
                if(frozenset({i}) == item):
                    count += 1
            if(count == 2):
                return True
        return False
    def calculate_itemsets_two(self, one_itemsets):
        print("Calculate itemsets with two products...")
        two_itemsets = defaultdict(int)
        for key, items in self.transactions.items():
            items = list(set(items))
            if (len(items) > 2):
                for perm in combinations(items, 2):
                    if self.has_support(perm, one_itemsets):
                        two_itemsets[frozenset(perm)] += 1
                    elif len(items) == 2:
                        if self.has_support(items, one_itemsets):
                            two_itemsets[frozenset(items)] += 1
        return two_itemsets
    def calculate_association_rules(self, one_itemsets, two_itemsets):
        print("Calculate association rules...")
        rules = []
        for source, source_freq in one_itemsets.items():
            for key, group_freq in two_itemsets.items():
                if source.issubset(key):
                    confidence = group_freq / source_freq
                    if(confidence >= self.min_conf):
                        target = key.difference(source)
                        support_a = source_freq / self.N
                        support_b = one_itemsets[target] / self.N
                        lift = confidence/support_b
                        rules.append((next(iter(source)), next(iter(target)), confidence, support_a, lift))
        return rules
    def make_rules(self):
        one_itemsets = self.calculate_itemsets_one()
        two_itemsets = self.calculate_itemsets_two(one_itemsets)
        self.rules = sorted(self.calculate_association_rules(one_itemsets,two_itemsets))
    def save_to_db(self):
        m = len(self.rules)
        if(m > 0):
            association_rules.delete_many({})
            all_rules = []
            temp = self.rules[0][0]
            form = {
                "product_id": temp,
                "associate_with":[
                    {
                        "product_id":self.rules[0][1],
                        "conf": self.rules[0][2],
                        "sup": self.rules[0][3]
                    }  
                ]

            }
            for i in range(1, m):
                if(self.rules[i][0] == temp):
                    form["associate_with"].append({
                        "product_id":self.rules[i][1],
                        "conf": self.rules[i][2],
                        "sup": self.rules[i][3]
                    })
                else:
                    all_rules.append(form)
                    temp = self.rules[i][0]
                    form = {
                        "product_id": temp,
                        "associate_with":[
                            {
                                "product_id":self.rules[i][1],
                                "conf": self.rules[i][2],
                                "sup": self.rules[i][3]
                            }  
                        ]

                    }
            all_rules.append(form)
            association_rules.insert_many(all_rules)
            print("DB had been saved")
    def describe_rules(self):
        print("Describe rules")
        for r in self.rules:
            x = products.find_one({'product_id':r[0]})
            y = products.find_one({'product_id':r[1]})
            print(x['name'], "----->", y['name'])
            print("Confident: {0}, Support: {1}, Lift: {2}".format(r[2], r[3], r[4]))
    @staticmethod
    def gennerate_recommend(product_id, user_trans = []):
        associate_with = []
        temp = association_rules.find({"product_id": product_id}, {"associate_with"})
        for t in temp:
            for i in t["associate_with"]:
                associate_with.append(i["product_id"])
        return associate_with
    def cold_start(self):
        self.generate_transactions()
        self.make_rules()
        self.describe_rules()
        self.save_to_db()
if __name__ == "__main__":
    #start
    start_time = time.time()
    #______________________________________________________________________________________
    temp = AssociationRules()
    temp.generate_transactions()
    temp.make_rules()
    temp.describe_rules()
    temp.save_to_db()
    print(temp.gennerate_recommend("1"))
    #end
    print(" Execute time: %s seconds" % (time.time() - start_time))
    #______________________________________________________________________________________


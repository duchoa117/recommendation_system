#import library
from collections import defaultdict
from tqdm import trange
from matplotlib import pyplot as plt
#___________________________________________________
#import module
from connect_mongodb import *
from recommendation_system import RecommendationSys, utils
#___________________________________________________
#code
class CF(RecommendationSys):
    def __init__(self, learning_rate = 0.05, lam = 0.5, iter=100):
        # lost value:
        self.L = 0
        # learning rate:
        self.learning_rate = learning_rate
        # lambda:
        self.lam = lam
        # iter:
        self.iter = iter
        # histogram
        self.his = {
            "loss_function": [],
        }
    def prepair_data(self):
        self.trans = pd.DataFrame(transactions.find({}, {"_id": 0, "total":0}))
        (m, n) = self.trans.shape
        for i in range(m):
            temp = self.trans.loc[i, "trans"]
            self.trans.loc[i, "products"] = [j for j in temp if temp[j] > 3]
        mu, sigma = 0, 0.1 # mean and standard deviation
        # users_matrix:
        self.user = defaultdict(lambda: None)
        self.item = defaultdict(lambda: None)
        for i in trange(self.trans.shape[0]):
            self.user[self.trans.loc[i, "user_id"]] = np.random.normal(mu, sigma, 10)
            for j in self.trans.loc[i, "products"]:
                if(self.item[j] is None):
                    self.item[j] = np.random.normal(mu, sigma, 10)
   
    def loss(self):
        self.L = 0
        (m, n) = self.trans.shape
        for i in range(m):
            user_vector = self.user[self.trans.loc[i, "user_id"]]
            for pro_id, rank in self.trans.loc[i, "trans"].items():
                if(rank >=3):
                    rank = 1
                else:
                    rank = 0
                item_vector = self.item[pro_id]
                self.L += 0.5*(user_vector.dot(item_vector.T) - rank)**2
                # add regularization
                self.L += 0.5*self.lam*(user_vector.dot(user_vector.T) + item_vector.dot(item_vector.T))
        self.L = self.L/int(m)
        
    def update_user(self, user_vector, item_vector, rank , pred):
        user_vector = user_vector - self.learning_rate*(pred*item_vector + self.lam*user_vector)
        # store user_vector in some where.....
        return user_vector
    def update_item(self, user_vector, item_vector, rank, pred):
        item_vector = item_vector - self.learning_rate*(pred*user_vector + self.lam*item_vector)
        # store item_vector in some where....
        return item_vector
    def fit(self, iter = None, alg = "basic"):
        if(iter != None):
            self.iter = iter
        (m, n) = self.trans.shape
        temp = int(self.iter/10)
        t = trange(self.iter, desc='Bar desc', leave=True)
        if(alg == "basic"):
            for x in t:
                for i in range(m):
                    user_vector = self.user[self.trans.loc[i, "user_id"]]
                    for pro_id, rank in self.trans.loc[i, "trans"].items():
                        if(rank >=3):
                            rank = 1
                        else: rank = 0
                        item_vector = self.item[pro_id]
                        pred = user_vector.dot(item_vector.T) - rank
                        self.user[self.trans.loc[i, "user_id"]] = self.update_user(user_vector, item_vector, rank, pred)
                        self.item[pro_id] = self.update_item(user_vector, item_vector, rank, pred)
                if(x%temp==0):
                    self.loss()
                    t.set_description("Cost Function: {0}".format(self.L))
                    t.refresh() # to show immediately the update
                    self.his["loss_function"].append(self.L)
        elif(alg == "fimf"):
            for x in trange(self.iter):
                for i in range(m):
                    user_vector = self.user[self.trans.loc[i, "user_id"]]
                    for pro_id, rank in self.trans.loc[i, "trans"].items():
                        if(rank >=3):
                            rank = 1
                        else:
                            rank = 0
                        item_vector = self.item[pro_id]
                        pred = user_vector.dot(item_vector.T) - rank
                        self.user[trans.loc[i, "user_id"]] = self.update_user(user_vector, item_vector, rank, pred)
                        self.item[pro_id] = self.update_item(user_vector, item_vector, rank, pred)
                if(x%temp==0):
                    self.loss()
                    self.print_loss()
                    self.his["loss_function"].append(self.L)
    def online_learning(self, user_id, item_id, rank):
        mu, sigma = 0, 0.1 # mean and standard deviation
        new_user = 0
        new_item = 0
        if(rank > 3):
            rank = 1
        else: 
            rank = 0
        if(self.user[user_id] is None):
            new_user = 1
            self.user[user_id] = np.random.normal(mu, sigma, 10)
        if(self.item[item_id] is None):
            new_item = 1
            self.item[item_id] = np.random.normal(mu, sigma, 10)
    
        user_vector = self.user[user_id]
        item_vector = self.item[item_id]        
        # clone new transaction
        # pass
        #____________________________________
        for i in trange(self.iter):
            pred = user_vector.dot(item_vector.T) - rank
            if(new_user == new_item):
                user_vector = self.update_user(user_vector, item_vector, rank, pred)
                item_vector = self.update_item(user_vector, item_vector, rank, pred)
            elif(new_user > new_item):
                user_vector = self.update_user(user_vector, item_vector, rank, pred)
            else:
                item_vector = self.update_item(user_vector, item_vector, rank, pred)
        # save data
        self.user[user_id] = user_vector
        self.item[item_id] = item_vector
    def genarate_recommend(self, user_id, user_trans=[]):
        user_id = str(user_id)
        u = self.user[user_id]
        r = pd.DataFrame(columns=["product_id", "rank"])
        for pro_id, pr_vector in self.item.items():
            r = r.append({"product_id":pro_id, "rank":u.dot(pr_vector.T)}, ignore_index=True)
        r = list(r.nlargest(5, 'rank')['product_id'])

        for t in r:
            if(t in user_trans):
                r.remove(t)
        return r
    def print_loss(self):
        print("loss:", self.L)
    def plot_his(self, c = "loss_function"):
        plt.plot(self.his[c])
        plt.show()
    def cold_start(self):
        self.prepair_data()
        self.fit()


if __name__ == "__main__":
    test = CF()
    test.prepair_data()
    test.fit()
    test.loss()
    test.print_loss()
    # test.plot_his()
    # triển khai bộ test:
    #new_user, old_item 
    # user_testset = defaultdict(lambda: None)
    # for i in range(test.trans.shape[0]):
    #     for pr in test.trans.loc[i, "products"]:
    #         user_testset["user"+pr] = pr
    # for i in user_testset:
    #     test.online_learning(i, user_testset[i], 5)



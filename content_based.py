#import library
from pyvi import ViTokenizer, ViPosTagger
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
import re
import time
import pandas as pd
#___________________________________________________
#import module
from connect_mongodb import *
from recommendation_system import RecommendationSys, utils
#___________________________________________________
#statics variables
PRODUCTS = None
VECTORIZER = TfidfVectorizer()
TEXTMATRIX = None

#___________________________________________________
#code
class ContentBased(RecommendationSys):
    @staticmethod
    def normalize_text(text):
        # link
        text = re.sub(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", ' <link> ', text, flags=re.MULTILINE)

        # email
        text = re.sub(r"[\w\.-]+@[\w\.-]+", ' <email> ', text, flags=re.MULTILINE)

        # image
        text = re.sub(r"(\w)*\.(?:jpg|gif|png)", ' <image> ', text, flags=re.MULTILINE)

        # atm       
        text = re.sub(r"\b\d{12,16}\b", ' <atm> ', text, flags=re.MULTILINE)

        # phone
        text = re.sub(r"\b\d{10,11}\b", ' <telephone> ', text, flags=re.MULTILINE)

        # price
        text = re.sub(r"\d+(k|l|K|L|\$|USD)", ' <money> ', text, flags=re.MULTILINE)

        # measure
        text = re.sub(r"\d+(cm|m|km|mm|g|kg)", ' <measure> ', text, flags=re.MULTILINE)

        # unusual
        text = re.sub(r"(/|\|\n\n|\n)", ' ', text, flags=re.MULTILINE)

        # emoji
        text = re.sub(
            u"([\U00002600-\U000027BF])|([\U0001f300-\U0001f64F])|([\U0001f680-\U0001f6FF])|([\U00010000-\U0010ffff])",
            ' <emoji> ', text, flags=re.MULTILINE)

        # Remove các ký tự kéo dài: vd: đẹppppppp
        text = re.sub(r'([A-Z])\1+', lambda m: m.group(1).upper(), text, flags=re.IGNORECASE)

        # Chuyển thành chữ thường
        text = text.lower()

        replace_list = {
            'òa': 'oà', 'óa': 'oá', 'ỏa': 'oả', 'õa': 'oã', 'ọa': 'oạ', 'òe': 'oè', 'óe': 'oé', 'ỏe': 'oẻ',
            'õe': 'oẽ', 'ọe': 'oẹ', 'ùy': 'uỳ', 'úy': 'uý', 'ủy': 'uỷ', 'ũy': 'uỹ', 'ụy': 'uỵ', 'uả': 'ủa',
            'ả': 'ả', 'ố': 'ố', 'u´': 'ố', 'ỗ': 'ỗ', 'ồ': 'ồ', 'ổ': 'ổ', 'ấ': 'ấ', 'ẫ': 'ẫ', 'ẩ': 'ẩ',
            'ầ': 'ầ', 'ỏ': 'ỏ', 'ề': 'ề', 'ễ': 'ễ', 'ắ': 'ắ', 'ủ': 'ủ', 'ế': 'ế', 'ở': 'ở', 'ỉ': 'ỉ',
            'ẻ': 'ẻ', 'àk': u' à ', 'aˋ': 'à', 'iˋ': 'ì', 'ă´': 'ắ', 'ử': 'ử', 'e˜': 'ẽ', 'y˜': 'ỹ', 'a´': 'á',

            # Chuẩn hóa 1 số sentiment words/English words
            'ô kêi': ' ok ', 'okie': ' ok ', ' o kê ': ' ok ',
            'okey': ' ok ', 'ôkê': ' ok ', 'oki': ' ok ', ' oke ': ' ok ', ' okay': ' ok ', 'okê': ' ok ',
            ' tks ': u' cám ơn ', 'thks': u' cám ơn ', 'thanks': u' cám ơn ', 'ths': u' cám ơn ', 'thank': u' cám ơn ',
            '⭐': 'star ', '*': 'star ', '🌟': 'star ', u'\n': ' ', u')': ' ', u'(': ' ',
            'kg ': u' không ', 'not': u' không ', u' kg ': u' không ', '"k ': u' không ', ' kh ': u' không ',
            'kô': u' không ', 'hok': u' không ', ' kp ': u' không phải ', u' kô ': u' không ', '"ko ': u' không ',
            u' ko ': u' không ', u' k ': u' không ', 'khong': u' không ', u' hok ': u' không ',
            ' vs ': u' với ', 'wa': ' quá ', 'wá': u' quá', 'j': u' gì ', '“': ' ',
            ' sz ': u' cỡ ', 'size': u' cỡ ', u' đx ': u' được ', 'dk': u' được ', 'dc': u' được ', 'đk': u' được ',
            'đc': u' được ', 'authentic': u' chuẩn chính hãng ', u' aut ': u' chuẩn chính hãng ',
            u' auth ': u' chuẩn chính hãng ', 'thick': u' positive ', 'store': u' cửa hàng ',
            'shop': u' cửa hàng ', 'sp': u' sản phẩm ', 'gud': u' tốt ', 'god': u' tốt ', 'wel done': ' tốt ',
            'good': u' tốt ', 'gút': u' tốt ',
            'sấu': u' xấu ', 'gut': u' tốt ', u' tot ': u' tốt ', u' nice ': u' tốt ', 'perfect': 'rất tốt',
            'bt': u' bình thường ',
            'time': u' thời gian ', 'qá': u' quá ', u' ship ': u' giao hàng ', u' m ': u' mình ', u' mik ': u' mình ',
            'ể': 'ể', 'product': 'sản phẩm', 'quality': 'chất lượng', 'chat': ' chất ', 'excelent': 'hoàn hảo',
            'bad': 'tệ', 'fresh': ' tươi ', 'sad': ' tệ ',
            'date': u' hạn sử dụng ', 'hsd': u' hạn sử dụng ', 'quickly': u' nhanh ', 'quick': u' nhanh ',
            'fast': u' nhanh ', 'delivery': u' giao hàng ', u' síp ': u' giao hàng ',
            'beautiful': u' đẹp tuyệt vời ', u' r ': u' rồi ', u' shopE ': u' cửa hàng ', u' order ': u' đặt hàng ',
            'chất lg': u' chất lượng ', u' sd ': u' sử dụng ', u' dt ': u' điện thoại ', u' nt ': u' nhắn tin ',
            u' tl ': u' trả lời ', u' sài ': u' xài ', u'bjo': u' bao giờ ',
            'thik': u' thích ', u' sop ': u' cửa hàng ', ' fb ': ' facebook ', ' face ': ' facebook ', ' very ': u' rất ',
            u'quả ng ': u' quảng  ',
            'dep': u' đẹp ', u' xau ': u' xấu ', 'delicious': u' ngon ', u'hàg': u' hàng ', u'qủa': u' quả ',
            'iu': u' yêu ', 'fake': u' giả mạo ', 'trl': 'trả lời', '><': u' positive ',
            ' por ': u' tệ ', ' poor ': u' tệ ', 'ib': u' nhắn tin ', 'rep': u' trả lời ', u'fback': ' feedback ',
            'fedback': ' feedback ',

            # các từ nghi vấn
            'nhỉ': ' <endturn> ', '?': ' <endturn> ', 'thế nào': ' <endturn> ', 'còn không': ' <endturn> ',
            'có không': ' <endturn> ', 'còn ko': ' <endturn> ', 'có ko': ' <endturn> ',
        }

        for k, v in replace_list.items():
            text = text.replace(k, v)
    #     # chuyen punctuation thành space
    #     translator = str.maketrans(string.punctuation, ' ' * len(string.punctuation))
    #     text = text.translate(translator)
        # remove nốt những ký tự thừa thãi
        text = text.replace(u'"', u' ')
        text = text.replace(u'️', u'')
        text = text.replace('🏻', '')
        text = text.strip()
        text = ViTokenizer.tokenize(text)
        return text
    @staticmethod 
    def pull_des():
        global PRODUCTS
        PRODUCTS = pd.DataFrame(list(products.find({}, {"product_id", "description"}))).drop(columns="_id")
    @staticmethod
    def update_des():
        pass
    @staticmethod
    def normalize_des():
        (m, n) = PRODUCTS.shape
        for i in range(m):
            PRODUCTS.loc[i, "description"] = ContentBased.normalize_text(
                                                PRODUCTS.loc[i, "description"])
    @staticmethod
    def vectorizer_text_model():
        global VECTORIZER
        global PRODUCTS
        VECTORIZER.fit(PRODUCTS['description'])
    @staticmethod
    def text_to_vector():
        global TEXTMATRIX
        global VECTORIZER
        global PRODUCTS
        TEXTMATRIX =  VECTORIZER.transform(PRODUCTS['description'])
    @staticmethod
    def gennerate_recommend(product_id, user_trans = []):
        cosine_sim = cosine_similarity(TEXTMATRIX)
        indices = pd.Series(PRODUCTS.loc[:, 'product_id'], )
        recommended_products = []
        idx = indices[indices == product_id].index[0]
        score_series = pd.Series(cosine_sim[idx]).sort_values(ascending = False)
        top_3_indexes = list(score_series.iloc[1:4].index)
        temp = list(PRODUCTS.loc[score_series.iloc[1:4].index, 'product_id'])
        count = 0
        for t in temp:
            if(t not in user_trans):
                recommended_products.append(t)
                count += 1
                if(count > 3): break
        return sample(recommended_products,2)
    @staticmethod
    def cold_start():
        ContentBased.pull_des()    
        ContentBased.normalize_des()    
        ContentBased.vectorizer_text_model()
        ContentBased.text_to_vector()
if __name__ == "__main__":
    #start
    start_time = time.time()
    #______________________________________________________________________________________

    ContentBased.pull_des()    
    ContentBased.normalize_des()    
    ContentBased.vectorizer_text_model()
    ContentBased.text_to_vector()
    t = ContentBased.gennerate_recommend("1")
    print(t)
    #end
    print(" Execute time: %s seconds" % (time.time() - start_time))
    #______________________________________________________________________________________





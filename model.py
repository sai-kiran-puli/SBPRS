from nltk.tokenize import word_tokenize
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet
from nltk.corpus import stopwords
import pickle, pandas as pd, numpy as np, re, string, nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('wordnet')
nltk.download('omw-1.4')

class SBPRS:
    MODEL = "bestmodel.pkl"
    TFIDF = "tfidf.pkl"
    RECOMMENDER = "recommendation.pkl"
    DATA = "data.pkl"

    def __init__(self):
        self.model = pickle.load(open(SBPRS.MODEL, 'rb'))
        self.tfidf = pd.read_pickle(SBPRS.TFIDF)
        self.user_final_rating = pickle.load(open(SBPRS.RECOMMENDER, 'rb'))
        self.data = pickle.load(open(SBPRS.DATA, 'rb'))
        self.lemmatizer = WordNetLemmatizer()
        self.stop_words = set(stopwords.words('english'))

    """function to filter the product recommendations using the sentiment model and get the top 5 recommendations"""

    def getRecommendations(self, user):
        if (user in self.user_final_rating.index):
            # get the product recommedation using the trained ML model
            recommendations = list(self.user_final_rating.loc[user].sort_values(ascending=False)[0:20].index)
            filtered_data = self.data[self.data.id.isin(recommendations)]
            # transform the input data using saved tf-idf vectorizer
            X = self.tfidf.transform(filtered_data["review_lemmatized"].values.astype(str))
            filtered_data["predicted_sentiment"] = self.model.predict(X)
            temp = filtered_data[['id', 'predicted_sentiment']]
            temp_grouped = temp.groupby('id', as_index=False).count()
            temp_grouped["pos_review_count"] = temp_grouped.id.apply(lambda x: temp[(
                temp.id == x) & (temp.predicted_sentiment == 1)]["predicted_sentiment"].count())
            temp_grouped["total_review_count"] = temp_grouped['predicted_sentiment']
            temp_grouped['pos_sentiment_percent'] = np.round(
                temp_grouped["pos_review_count"]/temp_grouped["total_review_count"]*100, 2)
            sorted_products = temp_grouped.sort_values(
                'pos_sentiment_percent', ascending=False)[0:5]
            return pd.merge(self.data, sorted_products, on="id")[["name", "brand", "manufacturer", "pos_sentiment_percent"]].drop_duplicates().sort_values(['pos_sentiment_percent', 'name'], ascending=[False, True])

        else:
            print(f"User name {user} doesn't exist")
            return None

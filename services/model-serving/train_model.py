# train_model.py
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
import joblib

texts = [
    "i am happy",
    "this is good",
    "i love it",
    "i am sad",
    "this is bad",
    "i hate this"
]

labels = ["positive", "positive", "positive", "negative", "negative", "negative"]

vec = CountVectorizer()
X = vec.fit_transform(texts)

model = LogisticRegression()
model.fit(X, labels)

joblib.dump((vec, model), "model.pkl")
print("Model saved to model.pkl")

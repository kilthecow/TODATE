import os
import pandas as pd
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "todo_priority.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")


def train():
    df = pd.read_csv(DATA_PATH)

    x = df["content"]
    y = df["priority"]

    model = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("classifier", LogisticRegression(max_iter=1000))
    ])

    model.fit(x, y)

    joblib.dump(model, MODEL_PATH)

    print("모델 학습 완료:", MODEL_PATH)


if __name__ == "__main__":
    train()
import os
import pandas as pd
import joblib
import mlflow
import mlflow.sklearn

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

    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("todo-priority-classification")

    with mlflow.start_run():

        model.fit(x, y)

        joblib.dump(model, MODEL_PATH)

        mlflow.log_param("model_type", "LogisticRegression")

        print("학습 완료")


if __name__ == "__main__":
    train()
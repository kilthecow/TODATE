import os
import pandas as pd
import joblib
import mlflow
import mlflow.sklearn

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_PATH = os.path.join(BASE_DIR, "data", "todo_priority.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")


def train():

    df = pd.read_csv(DATA_PATH)

    x = df["content"]
    y = df["priority"]

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42
    )

    model = Pipeline([
        ("tfidf", TfidfVectorizer()),
        ("classifier", LogisticRegression(max_iter=1000))
    ])

    mlflow.set_tracking_uri("file:./mlruns")
    mlflow.set_experiment("todo-priority-classification")

    with mlflow.start_run():

        model.fit(x_train, y_train)

        y_pred = model.predict(x_test)

        accuracy = accuracy_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred, average="weighted")

        joblib.dump(model, MODEL_PATH)

        mlflow.log_param("model_type", "LogisticRegression")
        mlflow.log_param("vectorizer", "TfidfVectorizer")
        mlflow.log_param("test_size", 0.2)
        mlflow.log_param("random_state", 42)

        mlflow.log_metric("accuracy", accuracy)
        mlflow.log_metric("f1_score", f1)

        mlflow.log_artifact(MODEL_PATH)

        mlflow.sklearn.log_model(model, "sklearn_model")

        print("학습 완료")
        print("accuracy:", accuracy)
        print("f1_score:", f1)
        print("model saved:", MODEL_PATH)


if __name__ == "__main__":
    train()
import os
import joblib


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")


def predict_priority(content):
    if not os.path.exists(MODEL_PATH):
        return "medium"

    model = joblib.load(MODEL_PATH)
    prediction = model.predict([content])[0]

    return prediction
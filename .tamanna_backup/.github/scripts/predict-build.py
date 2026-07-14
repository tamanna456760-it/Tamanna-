#!/usr/bin/env python3
import json
import os
import pickle
import sys

import numpy as np
import pandas as pd
from tensorflow.keras.layers import LSTM, Dense
from tensorflow.keras.models import Sequential

MODEL_FILE = "build_forecast_model.pkl"


def train():
    # Simulate training: in reality, fetch historical build data via GitHub API
    model = Sequential([LSTM(32, input_shape=(10, 1)), Dense(1, activation="sigmoid")])
    model.compile(optimizer="adam", loss="binary_crossentropy")
    # Dummy data: 1000 samples, 10 timesteps
    X = np.random.randn(1000, 10, 1)
    y = np.random.randint(0, 2, 1000)
    model.fit(X, y, epochs=5, verbose=0)
    with open(MODEL_FILE, "wb") as f:
        pickle.dump(model, f)
    print("✅ Model trained")


def predict():
    if not os.path.exists(MODEL_FILE):
        print("No model, assuming no failure")
        sys.exit(0)
    with open(MODEL_FILE, "rb") as f:
        model = pickle.load(f)
    # Use last 10 build outcomes (mock)
    X_test = np.random.randn(1, 10, 1)
    prob = model.predict(X_test)[0][0]
    if prob > 0.7:
        print("⚠️ Failure likely")
        sys.exit(1)
    else:
        print("✅ Build likely to pass")
        sys.exit(0)


if __name__ == "__main__":
    if "--train" in sys.argv:
        train()
    elif "--predict" in sys.argv:
        predict()

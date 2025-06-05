import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from notification_generator import generate_notification  # Make sure this file exists with generate_notification function

def extract_features(logs):
    """Convert logs into numerical features"""
    df = pd.DataFrame({
        "log_length": [len(log) for log in logs],
        "word_count": [len(log.split()) for log in logs],
        "error_flag": [1 if "error" in log.lower() else 0 for log in logs],
        "warning_flag": [1 if "warning" in log.lower() else 0 for log in logs]
    })

    vectorizer = TfidfVectorizer(max_features=100)
    tfidf_features = vectorizer.fit_transform(logs).toarray()

    features = np.hstack((df.values, tfidf_features))
    return features

def train_model():
    """Train an anomaly detection model using Isolation Forest"""
    with open("syslog_logs.txt", "r") as f:
        logs = [line.strip() for line in f.readlines()]

    features = extract_features(logs)

    model = IsolationForest(contamination=0.1, random_state=42)
    model.fit(features)

    predictions = model.predict(features)

    anomalies = [logs[i] for i in range(len(logs)) if predictions[i] == -1]

    with open("anomalies.txt", "w") as f:
        f.writelines("\n".join(anomalies))

    print(f"Anomalies saved to anomalies.txt")

    # Generate and display notifications for anomalies
    for i, pred in enumerate(predictions):
        if pred == -1:
            message = generate_notification(logs[i])
            print("\n🔔 Notification:", message)

if __name__ == "__main__":
    train_model()

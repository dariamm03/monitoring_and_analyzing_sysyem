import joblib
import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import hstack

class Predictor:
    def __init__(self):
        self.model = joblib.load('model.pkl')
        self.tfidf = joblib.load('tfidf.pkl')
        self.enc_user = joblib.load('enc_user.pkl')
        self.enc_proc = joblib.load('enc_proc.pkl')
        self.enc_sev = joblib.load('enc_sev.pkl')
        self.scaler = joblib.load('scaler.pkl')

    def preprocess(self, logs):
        df = pd.DataFrame(logs)
        df.fillna('', inplace=True)
        df['hour'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.hour.fillna(0).astype(int)
        df['weekday'] = pd.to_datetime(df['Timestamp'], errors='coerce').dt.weekday.fillna(0).astype(int)

        X_text = self.tfidf.transform(df['FormattedMessage'])
        user_encoded = self.enc_user.transform(df['UserName'])
        proc_encoded = self.enc_proc.transform(df['ProcessName'])
        sev_encoded = self.enc_sev.transform(df['Severity'])

        meta_features = pd.DataFrame({
            'user': user_encoded,
            'proc': proc_encoded,
            'sev': sev_encoded,
            'hour': df['hour'],
            'weekday': df['weekday']
        })

        meta_scaled = self.scaler.transform(meta_features)
        X_final = hstack([X_text, meta_scaled])
        return X_final

    def predict(self, logs):
        X = self.preprocess(logs)
        probs = self.model.predict_proba(X)[:, 1]
        return probs.tolist()

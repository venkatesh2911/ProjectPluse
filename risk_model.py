
import numpy as np
from sklearn.ensemble import RandomForestClassifier

FEATURES = [
    "cost_variance_percent","schedule_variance_percent","progress_gap",
    "financial_progress","expected_progress","milestone_delay_ratio",
    "expenditure_ratio","issues_count","previous_delay","contractor_rating"
]

def synthetic_label(row):
    score = (
        np.clip(row["cost_variance_percent"],0,35)*1.6 +
        np.clip(row["schedule_variance_percent"],0,35)*1.2 +
        np.clip(row["progress_gap"],0,40)*1.4 +
        row["milestone_delay_ratio"]*35 +
        min(row["issues_count"],15)*1.2 +
        row["previous_delay"]*7 +
        max(0,3.5-row["contractor_rating"])*8
    )
    return "High" if score >= 75 else ("Medium" if score >= 38 else "Low")

def train_model(df):
    labels = df.apply(synthetic_label, axis=1)
    model = RandomForestClassifier(n_estimators=180, random_state=42, class_weight="balanced")
    model.fit(df[FEATURES], labels)
    return model

def model_predict(model, df):
    return model.predict(df[FEATURES])

def feature_importance(model):
    return dict(zip(FEATURES, model.feature_importances_))


from pathlib import Path
import pandas as pd
import sqlite3

BASE = Path(__file__).resolve().parents[1]
CSV_PATH = BASE / "data" / "projects.csv"
DB_PATH = BASE / "data" / "projectpulse.db"

def load_projects():
    df = pd.read_csv(CSV_PATH)
    with sqlite3.connect(DB_PATH) as con:
        df.to_sql("projects", con, if_exists="replace", index=False)
    return df

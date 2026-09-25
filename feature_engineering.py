
import pandas as pd
import numpy as np

def engineer_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    out["cost_variance"] = out["current_cost"] - out["planned_cost"]
    out["cost_variance_percent"] = np.where(out["planned_cost"] > 0, out["cost_variance"]/out["planned_cost"]*100, 0)
    out["schedule_variance"] = out["elapsed_duration_months"] - (out["planned_duration_months"] * out["physical_progress"]/100)
    out["schedule_variance_percent"] = np.where(out["planned_duration_months"] > 0, out["schedule_variance"]/out["planned_duration_months"]*100, 0)
    out["progress_gap"] = out["expected_progress"] - out["physical_progress"]
    out["financial_progress_gap"] = out["financial_progress"] - out["physical_progress"]
    out["milestone_delay_ratio"] = np.where(out["milestones_total"] > 0, out["milestones_delayed"]/out["milestones_total"], 0)
    out["expenditure_ratio"] = np.where(out["planned_cost"] > 0, out["expenditure"]/out["planned_cost"], 0)
    out["delay_indicator"] = (out["progress_gap"] > 10).astype(int)
    out["issue_density"] = np.where(out["milestones_total"] > 0, out["issues_count"]/out["milestones_total"], 0)
    return out

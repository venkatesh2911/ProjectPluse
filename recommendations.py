
def recommendations(row, scores):
    rec=[]
    if row["cost_variance_percent"] > 10: rec.append("Review cost escalation and remaining budget.")
    if row["progress_gap"] > 15: rec.append("Review implementation schedule and delayed activities.")
    if row["milestone_delay_ratio"] > .30: rec.append("Identify critical delayed milestones.")
    if row["issues_count"] >= 6: rec.append("Conduct an issue-resolution review.")
    if row["schedule_variance_percent"] > 15: rec.append("Reassess remaining activities and completion timeline.")
    return rec or ["Continue routine monitoring against planned milestones."]

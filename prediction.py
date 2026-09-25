
import numpy as np

def risk_scores(row):
    clip = lambda x: float(np.clip(x,0,100))
    cost = clip(max(0,row["cost_variance_percent"])/30*100)
    time = clip(max(0,row["schedule_variance_percent"])/30*100)
    progress = clip(max(0,row["progress_gap"])/30*100)
    issue = clip(row["milestone_delay_ratio"]*100*.65 + min(row["issues_count"],15)/15*100*.35)
    overall = cost*.35 + time*.35 + progress*.20 + issue*.10
    level = lambda v: "High" if v>=70 else ("Medium" if v>=40 else "Low")
    return {"cost_score":round(cost,1),"time_score":round(time,1),"progress_score":round(progress,1),
            "issue_score":round(issue,1),"overall_score":round(overall,1),
            "cost_risk":level(cost),"time_risk":level(time),"overall_risk":level(overall)}

def top_drivers(row, scores):
    vals = {
        "Progress gap": max(0,row["progress_gap"]),
        "Cost variance": max(0,row["cost_variance_percent"]),
        "Milestone delays": row["milestone_delay_ratio"]*100,
        "Schedule variance": max(0,row["schedule_variance_percent"]),
        "Issue count": row["issues_count"]*3
    }
    return [k for k,v in sorted(vals.items(), key=lambda x:x[1], reverse=True)[:4]]

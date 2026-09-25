
def generate_warnings(row, scores):
    warnings=[]
    def add(sev, issue, evidence, action):
        warnings.append({"severity":sev,"issue":issue,"evidence":evidence,"action":action})
    if row["cost_variance_percent"] > 10:
        add("HIGH" if row["cost_variance_percent"]>18 else "MEDIUM",
            "Cost variance is above monitoring threshold.",
            f"Current cost is {row['cost_variance_percent']:.1f}% above plan.",
            "Review cost escalation and remaining budget.")
    if row["progress_gap"] > 15:
        add("HIGH" if row["progress_gap"]>22 else "MEDIUM",
            "Physical progress is significantly below expected progress.",
            f"Progress gap is {row['progress_gap']:.1f} percentage points.",
            "Review implementation schedule and delayed activities.")
    if row["milestone_delay_ratio"] > .30:
        add("HIGH" if row["milestone_delay_ratio"]>.45 else "MEDIUM",
            "Multiple project milestones are delayed.",
            f"{int(row['milestones_delayed'])} of {int(row['milestones_total'])} milestones are delayed.",
            "Identify critical delayed milestones.")
    if row["schedule_variance_percent"] > 15:
        add("HIGH" if row["schedule_variance_percent"]>25 else "MEDIUM",
            "Schedule deviation requires attention.",
            f"Schedule variance is {row['schedule_variance_percent']:.1f}%.",
            "Reassess remaining activities and completion timeline.")
    if scores["overall_score"] >= 70:
        add("HIGH","High-risk project requires management attention.",
            f"Overall demonstration risk score is {scores['overall_score']:.1f}/100.",
            "Prioritize a management review of the leading risk drivers.")
    if not warnings:
        add("LOW","No threshold breach detected.",
            "Current indicators remain within demo monitoring thresholds.",
            "Continue routine monitoring.")
    return warnings

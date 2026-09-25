
import streamlit as st
import pandas as pd
import plotly.express as px
from models.feature_engineering import engineer_features
from models.risk_model import train_model, model_predict, feature_importance
from models.prediction import risk_scores, top_drivers
from utils.data_loader import load_projects
from utils.risk_engine import generate_warnings
from utils.recommendations import recommendations
from utils.helpers import apply_style, money

st.set_page_config(page_title="ProjectPulse AI", page_icon="📊", layout="wide")
apply_style()

@st.cache_data
def get_data():
    return engineer_features(load_projects())

@st.cache_resource
def get_model():
    return train_model(get_data())

df = get_data()
model = get_model()
df["ml_risk"] = model_predict(model, df)

for k in ["cost_score","time_score","progress_score","issue_score","overall_score","cost_risk","time_risk","overall_risk"]:
    df[k] = [risk_scores(r)[k] for _, r in df.iterrows()]
df["drivers"] = df.apply(lambda r: top_drivers(r, risk_scores(r)), axis=1)

st.sidebar.markdown("## 📊 ProjectPulse AI")
st.sidebar.caption("SIH 2026 • SIH26103")
st.sidebar.info("Demo Environment — Synthetic Project Data")
page = st.sidebar.radio("Navigation", ["Overview","Projects","Risk Analysis","Early Warnings","Analytics","AI Assistant","About"])

st.markdown('<div class="hero"><h1>ProjectPulse AI</h1><p>Integrated project monitoring • predictive risk • transparent early warnings</p></div>', unsafe_allow_html=True)
st.caption("⚠️ Demonstration model trained on synthetic data. This is not an official government risk assessment and does not represent official MoSPI data.")

def kpi(label, value):
    st.markdown(f'<div class="kpi"><div class="label">{label}</div><div class="value">{value}</div></div>', unsafe_allow_html=True)

if page == "Overview":
    counts = df["overall_risk"].value_counts()
    cols = st.columns(6)
    vals = [
        ("Total Projects", len(df)), ("High Risk", int(counts.get("High",0))),
        ("Medium Risk", int(counts.get("Medium",0))), ("Low Risk", int(counts.get("Low",0))),
        ("Average Project Health", f"{100-df.overall_score.mean():.1f}%"),
        ("Projects With Alerts", int(sum(len(generate_warnings(r,risk_scores(r)))>0 for _,r in df.iterrows())))
    ]
    for col,(label,val) in zip(cols, vals):
        with col: kpi(label,val)

    a,b = st.columns(2)
    with a:
        st.plotly_chart(px.pie(df, names="overall_risk", title="Risk distribution", hole=.45), width="stretch")
    with b:
        tmp=df.sort_values("overall_score", ascending=False).head(12).copy()
        tmp["project"]=tmp.project_name.str.slice(0,28)
        st.plotly_chart(px.bar(tmp, x="overall_score", y="project", orientation="h", title="Highest demonstration risk scores", text="overall_score"), width="stretch")
    c,d,e=st.columns(3)
    with c: st.plotly_chart(px.histogram(df,x="cost_variance_percent",title="Cost variance %",nbins=12),width="stretch")
    with d: st.plotly_chart(px.histogram(df,x="schedule_variance_percent",title="Schedule variance %",nbins=12),width="stretch")
    with e: st.plotly_chart(px.scatter(df,x="expected_progress",y="physical_progress",color="overall_risk",hover_name="project_name",title="Physical vs expected progress"),width="stretch")

elif page == "Projects":
    st.subheader("Project Portfolio")
    c1,c2,c3,c4=st.columns(4)
    states=c1.multiselect("State",sorted(df.state.unique()))
    sectors=c2.multiselect("Sector",sorted(df.sector.unique()))
    risks=c3.multiselect("Risk level",["High","Medium","Low"])
    statuses=c4.multiselect("Project status",sorted(df.project_status.unique()))
    view=df.copy()
    if states: view=view[view.state.isin(states)]
    if sectors: view=view[view.sector.isin(sectors)]
    if risks: view=view[view.overall_risk.isin(risks)]
    if statuses: view=view[view.project_status.isin(statuses)]
    st.dataframe(view[["project_id","project_name","sector","state","cost_risk","time_risk","overall_risk","physical_progress","project_status"]].rename(columns={
        "project_id":"Project ID","project_name":"Project Name","sector":"Sector","state":"State",
        "cost_risk":"Cost Risk","time_risk":"Time Risk","overall_risk":"Overall Risk",
        "physical_progress":"Physical Progress","project_status":"Status"}),width="stretch",hide_index=True)
    options=view.project_id.tolist() or df.project_id.tolist()
    selected=st.selectbox("Open project detail",options)
    r=df[df.project_id==selected].iloc[0]; s=risk_scores(r)
    st.markdown(f"### {r.project_name} · {r.project_id}")
    x1,x2,x3,x4=st.columns(4)
    for col,label,val in [(x1,"Cost Risk",s["cost_risk"]),(x2,"Time Risk",s["time_risk"]),(x3,"Overall Risk",s["overall_risk"]),(x4,"Risk Score",f'{s["overall_score"]:.1f}/100')]:
        with col: kpi(label,val)
    a,b=st.columns(2)
    with a:
        st.markdown("#### Financial Information")
        st.write(f"Original cost: **{money(r.planned_cost)}**")
        st.write(f"Current cost: **{money(r.current_cost)}**")
        st.write(f"Variance: **{money(r.cost_variance)} ({r.cost_variance_percent:.1f}%)**")
        st.write(f"Expenditure: **{money(r.expenditure)}**")
        st.plotly_chart(px.bar(x=["Planned","Current"],y=[r.planned_cost,r.current_cost],title="Cost comparison"),width="stretch")
    with b:
        st.markdown("#### Progress & Timeline")
        st.progress(int(r.physical_progress),text=f"Physical progress: {r.physical_progress:.1f}%")
        st.progress(int(r.expected_progress),text=f"Expected progress: {r.expected_progress:.1f}%")
        st.write(f"Planned duration: **{r.planned_duration_months:.0f} months** · Elapsed: **{r.elapsed_duration_months:.1f} months**")
        st.write(f"Schedule variance: **{r.schedule_variance_percent:.1f}%**")
        st.plotly_chart(px.bar(x=["Expected","Actual"],y=[r.expected_progress,r.physical_progress],title="Progress comparison"),width="stretch")
    st.markdown("#### Top Risk Drivers")
    st.write(" • ".join(r.drivers))
    st.markdown("#### Early Warnings")
    for w in generate_warnings(r,s):
        st.markdown(f'<div class="alert {w["severity"].lower()}"><b>{w["severity"]}</b> · {w["issue"]}<br><span class="small">Evidence: {w["evidence"]}<br>Suggested action: {w["action"]}</span></div>',unsafe_allow_html=True)
    st.markdown("#### AI-generated Demonstration Recommendations")
    for x in recommendations(r,s): st.write("• "+x)
    st.caption("Recommendations are demonstration outputs, not official government instructions.")

elif page == "Risk Analysis":
    st.subheader("Risk Analysis")
    selected=st.selectbox("Select project",df.project_id)
    r=df[df.project_id==selected].iloc[0]; s=risk_scores(r)
    st.metric("Overall Risk Score",f'{s["overall_score"]:.1f}/100',delta=s["overall_risk"])
    a,b=st.columns(2)
    with a:
        st.plotly_chart(px.bar(x=["Cost","Time","Progress","Issue/Milestone"],y=[s["cost_score"],s["time_score"],s["progress_score"],s["issue_score"]],range_y=[0,100],title="Risk contribution scores"),width="stretch")
    with b:
        st.markdown("### Transparent weighting")
        st.write("Cost risk — **35%**"); st.write("Time risk — **35%**"); st.write("Progress risk — **20%**"); st.write("Issue/Milestone risk — **10%**")
        st.info("Thresholds: 0–39 Low · 40–69 Medium · 70–100 High")
    imp=feature_importance(model)
    impdf=pd.DataFrame({"Feature":list(imp),"Importance":list(imp.values())}).sort_values("Importance",ascending=False)
    st.plotly_chart(px.bar(impdf.head(10),x="Importance",y="Feature",orientation="h",title="Random Forest feature importance"),width="stretch")
    st.caption("Feature importance is a model-level explanation, not causal inference.")

elif page == "Early Warnings":
    st.subheader("Early Warning Center")
    filt=st.multiselect("Severity",["HIGH","MEDIUM","LOW"],default=["HIGH","MEDIUM"])
    alerts=[]
    for _,r in df.iterrows():
        for w in generate_warnings(r,risk_scores(r)):
            if w["severity"] in filt: alerts.append((r,w))
    for r,w in sorted(alerts,key=lambda x:{"HIGH":0,"MEDIUM":1,"LOW":2}[x[1]["severity"]]):
        st.markdown(f'<div class="alert {w["severity"].lower()}"><h4>{w["severity"]} · {r.project_name}</h4><b>{w["issue"]}</b><br>{w["evidence"]}<br><span class="small">Recommended action: {w["action"]}</span></div>',unsafe_allow_html=True)
    st.caption(f"{len(alerts)} alert(s) shown. Rules are transparent demo thresholds.")

elif page == "Analytics":
    st.subheader("Portfolio Analytics")
    a,b=st.columns(2)
    sector=df.groupby("sector",as_index=False).agg(avg_risk=("overall_score","mean"))
    state=df.groupby("state",as_index=False).agg(avg_risk=("overall_score","mean"))
    with a: st.plotly_chart(px.bar(sector.sort_values("avg_risk"),x="avg_risk",y="sector",orientation="h",title="Average risk by sector"),width="stretch")
    with b: st.plotly_chart(px.bar(state.sort_values("avg_risk"),x="avg_risk",y="state",orientation="h",title="Average risk by state"),width="stretch")
    st.plotly_chart(px.scatter(df,x="cost_variance_percent",y="schedule_variance_percent",size="overall_score",color="overall_risk",hover_name="project_name",title="Cost vs schedule risk landscape"),width="stretch")
    st.markdown("### Largest Progress Gaps")
    st.dataframe(df.nlargest(10,"progress_gap")[["project_name","sector","state","progress_gap","overall_score"]],width="stretch",hide_index=True)

elif page == "AI Assistant":
    st.subheader("Project Monitoring Assistant")
    st.caption("Local deterministic assistant — works without an API key.")
    q=st.text_input("Ask a question",placeholder="Which projects are high risk?")
    ql=q.lower().strip()
    if q:
        if "high risk" in ql:
            ans=df[df.overall_risk=="High"].sort_values("overall_score",ascending=False)
            st.write(f"**{len(ans)} high-risk projects:**")
            st.dataframe(ans[["project_id","project_name","sector","overall_score"]],width="stretch",hide_index=True)
        elif ("highest average cost" in ql) or ("sector" in ql and "cost variance" in ql):
            g=df.groupby("sector",as_index=False).cost_variance_percent.mean().sort_values("cost_variance_percent",ascending=False)
            st.write(f"Highest average cost variance sector in this demo dataset: **{g.iloc[0].sector} ({g.iloc[0].cost_variance_percent:.1f}%)**")
            st.dataframe(g,width="stretch",hide_index=True)
        elif "below 60" in ql:
            st.dataframe(df[df.physical_progress<60][["project_id","project_name","physical_progress","overall_risk"]],width="stretch",hide_index=True)
        elif "milestone" in ql and ("delay" in ql or "delayed" in ql):
            st.dataframe(df[df.milestone_delay_ratio>.30].sort_values("milestone_delay_ratio",ascending=False)[["project_id","project_name","milestones_delayed","milestones_total","milestone_delay_ratio"]],width="stretch",hide_index=True)
        else:
            term=ql.replace("project","").strip()
            match=df[df.project_name.str.lower().str.contains(term,na=False,regex=False)] if term else df.iloc[0:0]
            if len(match):
                r=match.iloc[0]
                st.write(f"**{r.project_name}** — {r.overall_risk} risk ({r.overall_score:.1f}/100).")
                st.write("Main drivers: "+", ".join(r.drivers))
                for x in recommendations(r,risk_scores(r)): st.write("• "+x)
            else:
                st.info("Try: “Which projects are high risk?”, “Which sector has the highest average cost variance?”, “Show projects with progress below 60%”, or “Which projects have major milestone delays?”")

elif page == "About":
    st.subheader("About ProjectPulse AI")
    st.markdown("""
    **SIH 2026 · SIH26103 · Smart Automation**

    ProjectPulse AI is a hackathon MVP for demonstrating how a web-based integrated project-monitoring platform can turn structured infrastructure project indicators into risk scores, early warnings, analytics and explainable recommendations.

    **Architecture:** CSV → Pandas feature engineering → Random Forest demonstration classifier + transparent risk engine → Streamlit/Plotly dashboard → SQLite persistence.

    **Data:** 48 reproducible synthetic infrastructure projects. No official or confidential government data is used.

    **Limitations:** Synthetic labels and indicators are not calibrated to government workflows; risk scores are demonstrations; no causal inference; no live departmental systems or external APIs.

    **Future scope:** role-based access, real project data connectors, document/NLP ingestion, GIS, time-series forecasting, model monitoring, human-in-the-loop approvals, audit logs and secure deployment.
    """)
    st.download_button("Download synthetic dataset",df.to_csv(index=False).encode(),"projects_demo.csv","text/csv")

st.sidebar.markdown("---")
st.sidebar.caption("ProjectPulse AI • Synthetic demo • SIH 2026")

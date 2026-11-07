import json
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Scholarship Advisory Rule-Based System",
    page_icon="🎓",
    layout="wide"
)

# Required Default JSON Rules (Exact schema as specified in Lab Report)
DEFAULT_RULES = [
    {
        "name": "Top merit candidate",
        "priority": 100,
        "conditions": [
            ["cgpa", ">=", 3.7],
            ["co_curricular_score", ">=", 80],
            ["family_income", "<=", 8000],
            ["disciplinary_actions", "==", 0]
        ],
        "action": {
            "decision": "AWARD FULL",
            "reason": "Excellent academic & co-curricular performance, with acceptable need"
        }
    },
    {
        "name": "Low CGPA not eligible",
        "priority": 95,
        "conditions": [
            ["cgpa", "<", 2.5]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "CGPA below minimum scholarship requirement"
        }
    },
    {
        "name": "Serious disciplinary record",
        "priority": 90,
        "conditions": [
            ["disciplinary_actions", ">=", 2]
        ],
        "action": {
            "decision": "REJECT",
            "reason": "Too many disciplinary records"
        }
    },
    {
        "name": "Good candidate partial scholarship",
        "priority": 80,
        "conditions": [
            ["cgpa", ">=", 3.3],
            ["co_curricular_score", ">=", 60],
            ["family_income", "<=", 12000],
            ["disciplinary_actions", "<=", 1]
        ],
        "action": {
            "decision": "AWARD PARTIAL",
            "reason": "Good academic & involvement record with moderate need"
        }
    },
    {
        "name": "Need-based review",
        "priority": 70,
        "conditions": [
            ["cgpa", ">=", 2.5],
            ["family_income", "<=", 4000]
        ],
        "action": {
            "decision": "REVIEW",
            "reason": "High need but borderline academic score"
        }
    }
]

def evaluate_condition(fact_value, operator, threshold):
    """Evaluates a single condition comparison."""
    if operator == ">=":
        return fact_value >= threshold
    elif operator == "<=":
        return fact_value <= threshold
    elif operator == ">":
        return fact_value > threshold
    elif operator == "<":
        return fact_value < threshold
    elif operator == "==":
        return fact_value == threshold
    elif operator == "!=":
        return fact_value != threshold
    return False

def run_rule_engine(facts, rules):
    """
    Evaluates applicant facts against rules sorted by priority (descending).
    Returns the action of the first rule whose conditions are all satisfied.
    """
    # Sort rules by priority (highest first)
    sorted_rules = sorted(rules, key=lambda r: r.get("priority", 0), reverse=True)
    
    for rule in sorted_rules:
        all_passed = True
        for condition in rule.get("conditions", []):
            fact_key, operator, threshold = condition
            fact_val = facts.get(fact_key)
            if fact_val is None or not evaluate_condition(fact_val, operator, threshold):
                all_passed = False
                break
        if all_passed:
            return rule["name"], rule["action"]
            
    return "Default Fallback", {
        "decision": "NOT ELIGIBLE",
        "reason": "Applicant does not satisfy criteria for available scholarship categories."
    }

# Interface Title & Description
st.title("🎓 University Scholarship Advisory System")
st.markdown("Knowledge Representation System (Rule-Based Engine)")

# Sidebar / Config Panel: JSON Rule Configuration
st.sidebar.header("⚙️ Knowledge Base (JSON Rules)")
st.sidebar.info("Rules are evaluated in order of **Priority** (Highest first).")

json_input = st.sidebar.text_area(
    "Edit Rules (JSON Format):",
    value=json.dumps(DEFAULT_RULES, indent=2),
    height=450
)

# Parse Rules from JSON Editor
try:
    active_rules = json.loads(json_input)
    st.sidebar.success("✓ Valid JSON Rules Loaded")
except Exception as e:
    st.sidebar.error(f"Invalid JSON Format: {e}")
    active_rules = DEFAULT_RULES

# Main Form: Applicant Facts Input
st.subheader("📋 Applicant Facts Entry")

col1, col2 = st.columns(2)

with col1:
    cgpa = st.number_input("Cumulative GPA (CGPA):", min_value=0.0, max_value=4.0, value=3.85, step=0.01)
    family_income = st.number_input("Monthly Family Income (RM):", min_value=0, value=5000, step=100)
    co_curricular_score = st.slider("Co-Curricular Involvement Score (0-100):", min_value=0, max_value=100, value=85)

with col2:
    disciplinary_actions = st.number_input("Disciplinary Actions on Record:", min_value=0, value=0, step=1)
    community_service_hours = st.number_input("Community Service Hours:", min_value=0, value=20, step=1)
    current_semester = st.number_input("Current Semester of Study:", min_value=1, max_value=12, value=3, step=1)

# Package Facts Dictionary
applicant_facts = {
    "cgpa": cgpa,
    "family_income": family_income,
    "co_curricular_score": co_curricular_score,
    "disciplinary_actions": disciplinary_actions,
    "community_service_hours": community_service_hours,
    "current_semester": current_semester
}

st.divider()

# Evaluation Trigger
if st.button("Evaluate Applicant Eligibility", type="primary"):
    rule_matched, result = run_rule_engine(applicant_facts, active_rules)
    
    st.subheader("📊 Decision Support Result")
    
    decision = result.get("decision", "PENDING")
    reason = result.get("reason", "N/A")
    
    if decision == "AWARD FULL":
        st.success(f"### Result: **{decision}**")
    elif decision == "AWARD PARTIAL":
        st.info(f"### Result: **{decision}**")
    elif decision == "REVIEW":
        st.warning(f"### Result: **{decision}**")
    else:
        st.error(f"### Result: **{decision}**")
        
    st.write(f"**Triggered Rule:** `{rule_matched}`")
    st.write(f"**Justification / Reason:** {reason}")
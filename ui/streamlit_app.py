import asyncio
import sys

# -------------------------------
# FIX: Windows asyncio subprocess
# -------------------------------
if sys.platform.startswith("win"):
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# -------------------------------
# LOAD ENV
# -------------------------------
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# -------------------------------
# FIX IMPORT PATH
# -------------------------------
sys.path.insert(0, str(Path(__file__).parent.parent))

# -------------------------------
# IMPORT RUN FUNCTION
# -------------------------------
from backend.test_executor import run

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(layout="wide", page_title="Playwright + LLM Automation")

# -------------------------------
# CSS
# -------------------------------
st.markdown("""
<style>
.stApp { background-color: #f8fafc; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #2563eb, #1e3a8a);
    color: white;
}

section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span {
    color: white !important;
}

/* Header */
.title {
    text-align: center;
    font-size: 40px;
    font-weight: 700;
    color: #1e293b;
}

.subtitle {
    text-align: center;
    color: #64748b;
    margin-bottom: 25px;
}

/* Buttons */
.stButton>button {
    background-color: #4f46e5;
    color: white;
    border-radius: 10px;
    height: 50px;
    font-size: 16px;
    border: none;
}
.stButton>button:hover {
    background-color: #4338ca;
}

/* Cards */
.card {
    background: white;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

/* Status */
.success { color: #16a34a; font-weight: 600; }
.fail { color: #dc2626; font-weight: 600; }

textarea {
    background-color: white !important;
    color: black !important;
}
</style>
""", unsafe_allow_html=True)

# -------------------------------
# SESSION STATE
# -------------------------------
if "result" not in st.session_state:
    st.session_state.result = None

if "scenario" not in st.session_state:
    st.session_state.scenario = ""

# -------------------------------
# SIDEBAR
# -------------------------------
st.sidebar.markdown("## ⚙️ Configuration")

headless = st.sidebar.checkbox("🕶️ Headless Mode", value=False)
debug_bool = st.sidebar.checkbox("🐞 Debug Mode", value=False)
debug = "true" if debug_bool else "false"

# -------------------------------
# HEADER
# -------------------------------
st.markdown('<div class="title">🎭 Playwright + LLM Automation</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">✨ AI-Powered Web Automation with Self-Healing Tests</div>', unsafe_allow_html=True)

# -------------------------------
# INPUT
# -------------------------------
st.markdown("### 🧠 Test Scenario")

scenario = st.text_area(
    "",
    height=150,
    placeholder="Go to website → login → add product → validate cart",
    value=st.session_state.scenario
)

# -------------------------------
# BUTTONS
# -------------------------------
col1, col2 = st.columns([3, 1])

run_clicked = col1.button("🚀 Run Automation", use_container_width=True)
clear_clicked = col2.button("🧹 Clear", use_container_width=True)

# -------------------------------
# CLEAR
# -------------------------------
if clear_clicked:
    st.session_state.result = None
    st.session_state.scenario = ""
    st.rerun()

# -------------------------------
# RUN
# -------------------------------
if run_clicked:
    if not scenario.strip():
        st.warning("⚠️ Please enter a scenario")
        st.stop()

    st.session_state.scenario = scenario

    with st.spinner("🤖 Running automation..."):
        try:
            res = run(scenario, headless, debug)
            st.session_state.result = res
        except Exception as e:
            st.error(f"❌ Execution Failed: {str(e)}")
            st.stop()

# -------------------------------
# DISPLAY RESULT
# -------------------------------
if st.session_state.result:

    res = st.session_state.result

    # -------------------------------
    # SUMMARY
    # -------------------------------
    st.markdown("### 📊 Execution Report")

    col1, col2, col3 = st.columns(3)

    status = res.get("status", "UNKNOWN")
    duration = res.get("duration", "-")
    error = res.get("error", None)

    with col1:
        color = "success" if status == "SUCCESS" else "fail"
        st.markdown(f'<div class="card">Status<br><span class="{color}">{status}</span></div>', unsafe_allow_html=True)

    with col2:
        st.markdown(f'<div class="card">Duration<br>{duration}</div>', unsafe_allow_html=True)

    with col3:
        if error:
            st.markdown(f'<div class="card fail">Error<br>{error}</div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="card success">No Errors</div>', unsafe_allow_html=True)

    # -------------------------------
    # CONSOLIDATED STEPS + CODE
    # -------------------------------
    st.markdown("### 🧪 Test Execution Details")

    steps = res.get("steps", [])

    clean_steps = []
    code_text = ""

    for step in steps:
        desc = step.get("description", "").strip()

        # ✅ CLEAN STEP TEXT (NO HTML / NO BULLETS)
        desc = desc.lstrip("-• ").replace("</div>", "").strip()
        clean_steps.append(desc)

        # ✅ CLEAN CODE
        code = step.get("code", "").strip()
        code_text += f"# Step {step.get('step_number')}\n{code}\n\n"

    steps_text = "\n\n".join(clean_steps)

    col1, col2 = st.columns(2)

    # -------------------------------
    # TEST STEPS (FIXED)
    # -------------------------------
    with col1:
        st.markdown("#### 📝 Test Steps")
        st.code(steps_text, language="markdown")

    # -------------------------------
    # CODE (SAFE)
    # -------------------------------
    with col2:
        st.markdown("#### 💻 Code")
        st.code(code_text, language="python")
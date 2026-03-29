import streamlit as st
import sys
import os
from pathlib import Path

# Add parent directory to path to import backend modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.test_executor import run_automation
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ╔═══════════════════════════════════════════════════════════════╗
# ║           PAGE CONFIGURATION & STYLING                        ║
# ╚═══════════════════════════════════════════════════════════════╝

st.set_page_config(
    page_title="🤖 Playwright + LLM Automation",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "About": "### 🤖 Intelligent Web Automation with Playwright + LLM\n\nAutomate complex web workflows using AI-powered code generation."
    }
)

# ╔═══════════════════════════════════════════════════════════════╗
# ║           CUSTOM CSS STYLING (COLORFUL)                       ║
# ╚═══════════════════════════════════════════════════════════════╝

st.markdown("""
    <style>
    /* Main background */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        color: white;
    }
    
    /* Headers */
    h1 {
        color: #667eea;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
        font-size: 2.5em;
    }
    
    h2 {
        color: #764ba2;
        border-bottom: 3px solid #667eea;
        padding-bottom: 10px;
    }
    
    h3 {
        color: #667eea;
    }
    
    /* Buttons */
    .stButton > button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 12px 30px;
        font-size: 16px;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.2s;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Input fields */
    .stTextArea > div > div > textarea {
        border-radius: 10px;
        border: 2px solid #667eea;
        padding: 10px;
        font-family: 'Monaco', 'Courier New', monospace;
    }
    
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 2px solid #667eea;
    }
    
    /* Success message */
    .success-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #38ef7d;
        margin: 10px 0;
    }
    
    /* Error message */
    .error-box {
        background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #f45c43;
        margin: 10px 0;
    }
    
    /* Info message */
    .info-box {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        margin: 10px 0;
    }
    
    /* Warning message */
    .warning-box {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #f5576c;
        margin: 10px 0;
    }
    
    /* Code blocks */
    code {
        background-color: rgba(102, 126, 234, 0.1);
        color: #667eea;
        padding: 2px 6px;
        border-radius: 5px;
        font-weight: bold;
    }
    
    /* Container styling */
    .stContainer {
        background: white;
        border-radius: 15px;
        padding: 20px;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin: 10px 0;
    }
    
    /* Metric styling */
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════════════════╗
# ║           SIDEBAR - CONFIGURATION                             ║
# ╚═══════════════════════════════════════════════════════════════╝

with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    
    headless_mode = st.checkbox("🤫 Headless Mode (No browser window)", value=False)
    enable_debug = st.checkbox("🐛 Enable Debug Logs", value=True)
    
    st.markdown("---")
    st.markdown("### 📚 Quick Start")
    st.markdown("""
    1. Enter your test scenario
    2. Click **Run Automation**
    3. Watch the browser execute
    4. View results below
    """)
    
    st.markdown("---")
    st.markdown("### 🔗 Resources")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("[📖 Playwright Docs](https://playwright.dev/python/)")
    with col2:
        st.markdown("[🔑 OpenAI API](https://platform.openai.com/)")
    
    st.markdown("---")
    st.markdown("### 📊 Session Info")
    if os.getenv("OPENAI_API_KEY"):
        st.success("✅ OpenAI API Key: Configured")
    else:
        st.error("❌ OpenAI API Key: Missing (.env file)")

# ╔═══════════════════════════════════════════════════════════════╗
# ║           MAIN PAGE HEADER                                    ║
# ╚═══════════════════════════════════════════════════════════════╝

st.markdown("""
    <div style='text-align: center; margin-bottom: 30px;'>
        <h1>🎭 Playwright + LLM Automation</h1>
        <p style='font-size: 18px; color: #764ba2; margin-top: -10px;'>
            ✨ AI-Powered Web Automation with Self-Healing Tests
        </p>
    </div>
    """, unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════════════════╗
# ║           SESSION STATE INITIALIZATION                        ║
# ╚═══════════════════════════════════════════════════════════════╝

if "execution_in_progress" not in st.session_state:
    st.session_state.execution_in_progress = False

if "execution_result" not in st.session_state:
    st.session_state.execution_result = None

# ╔═══════════════════════════════════════════════════════════════╗
# ║           MAIN CONTENT AREA                                   ║
# ╚═══════════════════════════════════════════════════════════════╝

col1, col2 = st.columns([2, 1])

with col1:
    st.markdown("### 📝 Test Scenario")
    st.markdown("Describe the automation flow you want to execute:")
    
    scenario_input = st.text_area(
        label="Scenario",
        value="""Go to https://practice.qabrains.com/ecommerce/login
Validate add to cart flow for any product
Here is high level steps to achieve this:
open page, login with test@qabrains.com & Password123,
Add 1st product to cart, check the cart and validate product is added successfully""",
        height=150,
        label_visibility="collapsed",
        placeholder="Enter your test scenario here..."
    )

with col2:
    st.markdown("### 🎯 Example Scenarios")
    st.markdown("""
    #### 🛒 E-commerce
    - Login flow
    - Add to cart
    - Checkout
    
    #### 📝 Forms
    - Fill registration
    - Submit forms
    - Validate success
    
    #### 🔍 Navigation
    - Search products
    - Filter results
    - View details
    """)

# ╔═══════════════════════════════════════════════════════════════╗
# ║           EXECUTION SECTION                                   ║
# ╚═══════════════════════════════════════════════════════════════╝

st.markdown("---")

col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

with col_btn1:
    if st.button("🚀 Run Automation", use_container_width=True):
        if not scenario_input.strip():
            st.error("❌ Please enter a scenario first!")
        elif not os.getenv("OPENAI_API_KEY"):
            st.error("❌ OPENAI_API_KEY not configured in .env file")
        else:
            st.session_state.execution_in_progress = True

with col_btn2:
    if st.button("🔄 Clear Results", use_container_width=True):
        st.session_state.execution_result = None
        st.rerun()

with col_btn3:
    if st.button("ℹ️ Show Info", use_container_width=True):
        st.info("""
        ### 🤖 How It Works
        
        1. **Scenario Input** → Your test description
        2. **Browser Launch** → Playwright opens browser
        3. **DOM Extraction** → Smart element detection
        4. **Code Generation** → LLM generates Playwright code
        5. **Execution** → Code runs on the page
        6. **Error Handling** → Auto-fix on failure
        7. **Repeat** → Until test complete or fails
        """)

# ╔═══════════════════════════════════════════════════════════════╗
# ║           EXECUTION PROGRESS                                  ║
# ╚═══════════════════════════════════════════════════════════════╝

if st.session_state.execution_in_progress:
    st.markdown("---")
    
    with st.container():
        progress_placeholder = st.empty()
        logs_placeholder = st.empty()
        result_placeholder = st.empty()
        
        with progress_placeholder.container():
            st.markdown("""
                <div class='info-box'>
                    <h3>⏳ Running Automation...</h3>
                    <p>Browser is executing your scenario. This may take 30-60 seconds.</p>
                </div>
                """, unsafe_allow_html=True)
        
        try:
            with logs_placeholder.container():
                st.write("")
                with st.spinner("🎬 Launching browser..."):
                    st.write("Initializing Playwright...")
                    st.write("Navigating to target URL...")
                    st.write("Extracting page elements...")
                    st.write("Generating step code with LLM...")
                    st.write("Executing automation steps...")
            
            # Call backend execution function
            result = run_automation(
                scenario=scenario_input,
                headless=headless_mode,
                debug=enable_debug
            )
            
            st.session_state.execution_result = result
            st.session_state.execution_in_progress = False
            
            # Clear placeholders and show result
            progress_placeholder.empty()
            logs_placeholder.empty()
            
            if result.get("status") == "SUCCESS":
                with result_placeholder.container():
                    st.markdown("""
                        <div class='success-box'>
                            <h3>✅ Automation Completed Successfully!</h3>
                            <p>Your test scenario has been executed successfully.</p>
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.write("**📊 Execution Summary:**")
                    col_s1, col_s2, col_s3 = st.columns(3)
                    with col_s1:
                        st.metric("Steps Executed", result.get("steps", 0))
                    with col_s2:
                        st.metric("Errors Fixed", result.get("errors_fixed", 0))
                    with col_s3:
                        st.metric("Duration", result.get("duration", "N/A"))
                    
                    if result.get("description"):
                        st.write("**📝 Final Output:**")
                        st.write(result.get("description"))
            
            else:
                with result_placeholder.container():
                    st.markdown(f"""
                        <div class='error-box'>
                            <h3>❌ Automation Failed</h3>
                            <p>{result.get('error', 'Unknown error occurred')}</p>
                        </div>
                        """, unsafe_allow_html=True)
        
        except Exception as e:
            progress_placeholder.empty()
            logs_placeholder.empty()
            with result_placeholder.container():
                st.markdown(f"""
                    <div class='error-box'>
                        <h3>❌ Error During Execution</h3>
                        <p>{str(e)}</p>
                    </div>
                    """, unsafe_allow_html=True)

# ╔═══════════════════════════════════════════════════════════════╗
# ║           DISPLAY PREVIOUS RESULTS                            ║
# ╚═══════════════════════════════════════════════════════════════╝

if st.session_state.execution_result and not st.session_state.execution_in_progress:
    st.markdown("---")
    st.markdown("### 📈 Last Execution Result")
    
    result = st.session_state.execution_result
    
    if result.get("status") == "SUCCESS":
        st.markdown("""
            <div class='success-box'>
                <h3>✅ Execution Successful</h3>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
            <div class='error-box'>
                <h3>❌ Execution Failed</h3>
            </div>
            """, unsafe_allow_html=True)
    
    col_res1, col_res2, col_res3 = st.columns(3)
    with col_res1:
        st.metric("Status", result.get("status", "Unknown"))
    with col_res2:
        st.metric("Attempts", result.get("attempts", 0))
    with col_res3:
        st.metric("Last Updated", "Just now")

# ╔═══════════════════════════════════════════════════════════════╗
# ║           FOOTER                                              ║
# ╚═══════════════════════════════════════════════════════════════╝

st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #764ba2; margin-top: 30px;'>
        <small>
        🚀 Built with <b>Playwright</b> + <b>LLM (GPT-4o-mini)</b> + <b>LangSmith</b>
        </small>
        <br>
        <small>
        📚 <a href='https://playwright.dev/python/'>Playwright Docs</a> | 
        <a href='https://platform.openai.com/docs/api-reference'>OpenAI API</a> | 
        <a href='https://docs.smith.langchain.com/'>LangSmith Docs</a>
        </small>
    </div>
    """, unsafe_allow_html=True)

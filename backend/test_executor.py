import os
import re
import time
import asyncio
from dotenv import load_dotenv
from playwright.sync_api import sync_playwright
from playwright.sync_api import expect
from backend.utils.logger import add_debug_logs
from backend.playwright.page_functions import wait_for_dom_change, extract_dom_tree
from backend.agents.code_mender.agent import fix_error_code_with_llm
from backend.agents.code_weaver.agent import generate_step_code
from langsmith import traceable

# ✅ Load env
load_dotenv()



def execute_code_with_retry(page, llmResult, elements, retry):
    """Execute code with automatic retry on failure"""
    globals = {"page": page, "expect": expect}
    locals = {}
    code = llmResult["code"]
    stepDesc = llmResult["description"]
    is_fixed = False

    # Throw exception when no code found to execute
    if not code:
        # Execute actions
        add_debug_logs("\n❌ No code returned by LLM. Description:\n", stepDesc)
        raise Exception("LLM Not returned any code to execute. Reason: " + stepDesc)

    try:        
        print(f"🚀 Executing {stepDesc}:")
        add_debug_logs("Code:\n", code)
        exec(code, globals, locals)         

    except Exception as e:
        print("\n❌ Failed:", str(e))
        if not retry:
            print("\n❌ Not retrying as retry flag is False.")
            raise e
        
        print("\n❌ Failed code: \n", code)
        
        print("\n🔁 Retrying with LLM fix...\n")

        result = fix_error_code_with_llm(str(e), code, elements)
        print("\n✅ info from LLM:\n", result["description"])
        print("\n✅ Retried code: \n", result["code"])
        is_fixed = True
        code = result["code"]  # Update code to the fixed version
        execute_code_with_retry(page, result, elements, retry=False)
        
    
    print("\n✅ Step Execution Passed")
    print("=" * 30)
    
    return {
        "code": code,
        "description": stepDesc,
        "is_fixed": is_fixed
    }
    

# -------------------------------
# ✅ MAIN - MODIFIED FOR STREAMLIT
# -------------------------------
@traceable(name="Chat Pipeline")
def run(scenario, headless=False, debug=None):
    
    """
    Execute automation with custom scenario
    
    Args:
        scenario (str): Test scenario description
        headless (bool): Run browser in headless mode
        debug (bool|None): Enable debug logging. If None, uses DEBUG from .env
    
    Returns:
        dict: Result containing status, history, code, etc.
    """
    # Set DEBUG environment variable (add_debug_logs checks this)
    if debug is not None:
        os.environ["DEBUG"] = "true" if debug else "false"
    
    start_time = time.time()
    execution_history = []
    generated_code_steps = []
    final_status = "FAIL"
    
    try:
        # Handle event loop for Windows/Streamlit compatibility
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If loop is running (Streamlit), create new event loop
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=headless)
            page = browser.new_page()

            # Extract URL from scenario
            url_match = re.search(r'https?://[^\s]+', scenario)
            if not url_match:
                return {
                    "status": "FAIL",
                    "error": "No URL found in scenario",
                    "history": [],
                    "generated_code": [],
                    "duration": f"{time.time() - start_time:.2f}s"
                }
            
            target_url = url_match.group(0).split()[0]  # Get clean URL
            
            # Open page
            page.goto(target_url)

            while True:
                # Wait properly
                wait_for_dom_change(page)
                
                # Extract elements
                elements = extract_dom_tree(page)

                # add_debug_logs checks DEBUG env var automatically
                add_debug_logs("\n🔍 Elements On Load:\n", elements)

                if not elements:
                    raise Exception("❌ No elements found on page")

                # Generate action code
                result = generate_step_code(elements, scenario, execution_history)
                status = result["status"]
                description = result["description"]
                generated_code = result["code"]

                # Store step info
                step_info = {
                    "step_number": len(generated_code_steps) + 1,
                    "description": description,
                    "code": generated_code,
                    "status": status
                }

                # Execute actions
                try:
                    exec_result = execute_code_with_retry(page, result, elements, retry=True)
                    step_info["code"] = exec_result["code"]
                    step_info["is_fixed"] = exec_result["is_fixed"]
                except Exception as e:
                    step_info["error"] = str(e)
                    print(f"\n❌ Step failed: {e}")

                # Store execution tracking
                execution_history.append(description)
                generated_code_steps.append(step_info)

                # Print progress
                print(f"\n📍 Step {len(generated_code_steps)}: {description}")

                # ------------------------
                # TERMINAL STATES
                # ------------------------
                if status == "FAIL":
                    print("\n❌ TEST FAILED")
                    final_status = "FAIL"
                    break
                elif status == "COMPLETE":
                    print("\n✅ TEST PASSED") 
                    final_status = "SUCCESS"
                    break
                    
            browser.close()
            
            return {
                "status": final_status,
                "steps": generated_code_steps,
                "duration": f"{time.time() - start_time:.2f}s"
            }
    
    except Exception as e:
        return {
            "status": "FAIL",
            "error": str(e),
            "steps": generated_code_steps,
            "duration": f"{time.time() - start_time:.2f}s"
        }



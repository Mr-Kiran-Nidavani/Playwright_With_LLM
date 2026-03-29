import os
import re
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



# SCENARIO = """
# Go to https://practice.qabrains.com
# on regiistration completion, verify success message
# Here is high level steps to achieve this:
# open page, go to registration, fill form, submit, validate success
# """

SCENARIO = """
Go to https://practice.qabrains.com/ecommerce/login
Validate add to cart flow for any product
Here is high level steps to achieve this:
open page, login with test@qabrains.com & Password123,
Add 1st product to cart, check the cart and validate product is added successfully
"""

# SCENARIO = """
# Go to https://purchase-stest.allstate.com/onlineshopping/welcome
# Validate able generate auto quote
# select auto product and provide zip 60606
# """


def execute_code_with_retry(page, llmResult, elements, retry):
    globals = {"page": page, "expect": expect}
    locals = {}
    code = llmResult["code"]
    stepDesc = llmResult["description"]

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
        execute_code_with_retry(page, result, elements, retry=False)
        
    
    print("\n✅ Step Execution Passed")
    print("=" * 30)
    

# -------------------------------
# ✅ MAIN
# -------------------------------
@traceable(name="Chat Pipeline")
def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        # Open page
        page.goto("https://practice.qabrains.com/ecommerce/login")

        history = []

        while True:
            # Wait properly
            wait_for_dom_change(page)
            
            # Extract elements
            elements = extract_dom_tree(page)

            add_debug_logs("\n🔍 Elements On Load:\n", elements)

            if not elements:
                raise Exception("❌ No elements found")

            # Generate action code
            result = generate_step_code(elements, SCENARIO, history)
            status = result["status"]
            description = result["description"]

            # Execute actions
            execute_code_with_retry(page, result, elements, retry=True)
            history.append(description)


            # ------------------------
            # TERMINAL STATES
            # ------------------------
            if status == "FAIL":
                print("\n❌ TEST FAILED")
                break
            elif status == "COMPLETE":
                print("\n✅ TEST PASSED") 
                break        
                

      
        input("\nPress Enter to close browser...")
        browser.close()



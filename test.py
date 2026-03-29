from backend.test_executor import run





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

res = run(SCENARIO)

print(f"\n\nFinal Result:\n", res)
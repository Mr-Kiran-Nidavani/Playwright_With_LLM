
def get_prompt(error, code, elements):
    
    return f"""
Fix this Playwright code.

Error:
{error}

Code:
{code}

Elements:
{elements}

Rules:
- Fix selector ambiguity
- Ensure uniqueness
- Return ONLY corrected Python code

-------------------------------
OUTPUT FORMAT (STRICT):
-------------------------------
status: <COMPLETE | FAIL | AWAITING>

code:
<ONLY executable Playwright Python code>

description:
<Short explanation of action taken OR reason if FAIL>
"""
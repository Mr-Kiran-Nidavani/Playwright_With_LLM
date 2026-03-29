import re


# -------------------------------
# ✅ UTILITIES
# -------------------------------
def parse_llm_response(response: str) -> dict:
    """
    Parses LLM response into:
    {
        "status": str,
        "code": str,
        "description": str
    }
    """

    if not response:
        return {
            "status": "FAIL",
            "code": "",
            "description": "Empty LLM response"
        }

    # -------------------------------
    # 1. Remove markdown safely
    # -------------------------------
    response = re.sub(r"```python", "", response, flags=re.IGNORECASE)
    response = re.sub(r"```", "", response)
    response = response.strip()

    # -------------------------------
    # 2. Extract fields safely
    # -------------------------------
    status_match = re.search(r"status\s*:\s*(\w+)", response, re.IGNORECASE)
    code_match = re.search(r"code\s*:\s*(.*?)(?:\n\s*description\s*:|\Z)", response, re.IGNORECASE | re.DOTALL)
    desc_match = re.search(r"description\s*:\s*(.*)", response, re.IGNORECASE | re.DOTALL)

    status = status_match.group(1).upper() if status_match else "FAIL"
    code = code_match.group(1).strip() if code_match else ""
    description = desc_match.group(1).strip() if desc_match else ""

    # -------------------------------
    # 3. Normalize status
    # -------------------------------
    if status not in {"COMPLETE", "FAIL", "AWAITING"}:
        status = "FAIL"
        description = f"Invalid status returned by LLM. Raw: {response}"

    # -------------------------------
    # 4. Safety checks
    # -------------------------------
    if status == "FAIL" and not description:
        description = "LLM marked FAIL but no reason provided"

    if status != "FAIL" and not code:
        return {
            "status": "FAIL",
            "code": "",
            "description": "Missing code for non-FAIL status"
        }

    # -------------------------------
    # 5. Final clean of code
    # -------------------------------
    code = code.strip()

    return {
        "status": status,
        "code": code,
        "description": description
    }



from .prompt import get_prompt
from backend.llm.client import client
from backend.llm.utils import parse_llm_response


# -------------------------------
# ✅ LLM: FIX CODE
# -------------------------------

def fix_error_code_with_llm(error, code, elements):
    prompt = get_prompt(error, code, elements)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return parse_llm_response(response.choices[0].message.content)

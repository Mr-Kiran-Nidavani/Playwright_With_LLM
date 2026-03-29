
from .prompt import get_prompt
from backend.llm.client import client
from backend.llm.utils import parse_llm_response

# -------------------------------
# ✅ LLM: ACTION CODE
# -------------------------------

def generate_step_code(elements, scenario, history):
    prompt = get_prompt(elements, scenario, history)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    return parse_llm_response(response.choices[0].message.content)

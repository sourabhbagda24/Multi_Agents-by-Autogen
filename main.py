import os
import time
from dotenv import load_dotenv
from google import genai
from google.genai import errors
from autogen import ConversableAgent, UserProxyAgent

# ---------------- Gemini setup ----------------
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY not found. Add it to your .env file.")

MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")
# Primary model busy ho to in models ko try karega (apne account ke hisaab se badal sakte ho)
FALLBACK_MODELS = [m.strip() for m in os.getenv("GEMINI_FALLBACKS", "").split(",") if m.strip()]

client = genai.Client(api_key=GEMINI_API_KEY)


def gemini_chat(prompt: str, max_retries: int = 5) -> str:
    models_to_try = [MODEL_NAME] + FALLBACK_MODELS
    last_error = None

    for model_name in models_to_try:
        for attempt in range(max_retries):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )
                return response.text
            except errors.ServerError as e:  # 503 / 500 etc.
                last_error = e
                wait = 2 ** attempt  # 1, 2, 4, 8, 16 seconds
                print(f"[{model_name}] server busy (attempt {attempt + 1}/{max_retries}), "
                      f"retrying in {wait}s...")
                time.sleep(wait)
            except errors.ClientError as e:
                # 429 = rate limit, retry; baaki (404, 400) pe turant next model
                if getattr(e, "code", None) == 429:
                    last_error = e
                    wait = 2 ** attempt * 2
                    print(f"[{model_name}] rate limited, retrying in {wait}s...")
                    time.sleep(wait)
                else:
                    last_error = e
                    print(f"[{model_name}] error: {e}")
                    break

    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")

# ---------------- Custom Gemini Agent ----------------
class GeminiAgent(ConversableAgent):
    """AutoGen agent whose replies come from Gemini instead of OpenAI."""

    def __init__(self, name, system_prompt="", **kwargs):
        super().__init__(name, llm_config=False, human_input_mode="NEVER", **kwargs)
        self.system_prompt = system_prompt

    def generate_reply(self, messages=None, sender=None, **kwargs):
        prompt = "\n".join(m["content"] for m in (messages or []))
        if self.system_prompt:
            prompt = f"{self.system_prompt}\n\n{prompt}"
        return {"role": "assistant", "content": gemini_chat(prompt)}


# ---------------- Initialize agents ----------------
user_proxy = UserProxyAgent(
    name="User",
    human_input_mode="NEVER",
    code_execution_config=False,
)

analyst = GeminiAgent(name="AnalystBot", system_prompt="You are a sharp business analyst.")
swot = GeminiAgent(name="SWOTBot", system_prompt="You are an expert in SWOT analysis.")
strategist = GeminiAgent(name="StrategistBot", system_prompt="You are a growth strategy consultant.")
critic = GeminiAgent(name="CriticBot", system_prompt="You are a tough but constructive strategy critic.")

# ---------------- Business description (input) ----------------
business_description = """
Our company is a 2-year-old startup that provides AI-powered resume screening software for
HR teams.
We've gained traction in India but are struggling to expand internationally.
The product integrates with common HR tools and uses machine learning to rank candidates.
We face growing competition and challenges in compliance and data privacy in
international markets.
"""


# ---------------- Chain agents ----------------
def ask(agent, instruction, context):
    messages = [{"role": "user", "content": f"{instruction}\n\n{context}"}]
    return agent.generate_reply(messages, sender=user_proxy)["content"]


def main():
    # Step 1: AnalystBot
    analyst_output = ask(
        analyst,
        "Analyze the following business and identify key challenges and strengths:",
        business_description,
    )
    print("AnalystBot Output:\n", analyst_output)

    # Step 2: SWOTBot
    swot_output = ask(
        swot,
        "Based on this analysis, provide a detailed SWOT analysis:",
        analyst_output,
    )
    print("\nSWOTBot Output:\n", swot_output)

    # Step 3: StrategistBot
    strategies_output = ask(
        strategist,
        "Based on this SWOT analysis, suggest 3 business growth strategies:",
        swot_output,
    )
    print("\nStrategistBot Output:\n", strategies_output)

    # Step 4: CriticBot
    critic_output = ask(
        critic,
        "Critique the following strategies and suggest improvements:",
        strategies_output,
    )
    print("\nCriticBot Output:\n", critic_output)

    report = f"""# Business Analysis Report

## Analyst
{analyst_output}

## SWOT
{swot_output}

## Strategies
{strategies_output}

## Critique
{critic_output}
"""
    with open("report.md", "w", encoding="utf-8") as f:
        f.write(report)
    print("\nSaved to report.md")
if __name__ == "__main__":
    main()
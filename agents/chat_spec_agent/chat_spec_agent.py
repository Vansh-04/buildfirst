import json
import os
import re
from google import genai

DRAFT_STATE = "conversation_state.json"


class ChatSpecAgent:
    """
    LLM-driven Conversation Agent.
    Acts as Product Manager + Architect.
    NEVER builds. NEVER auto-approves.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("❌ GEMINI_API_KEY not set")

        self.client = genai.Client(api_key=api_key)
        self.model = "models/gemini-2.5-flash"

    # ---------------- PUBLIC ----------------

    def run(self, user_message: str):
        state = self._load_state()

        # Explicit approval check
        if user_message.strip().lower() in {"yes", "yes build", "build it", "go"}:
            state["status"] = "approved"
            self._save_state(state)
            return state

        prompt = self._build_prompt(state, user_message)

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        text = response.text.strip()
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("LLM did not return valid JSON")

        update = json.loads(match.group())

        # Merge safely
        state["status"] = update.get("status", state["status"])
        state["current_plan"] = update.get("current_plan", state["current_plan"])
        state["suggested_features"] = update.get("suggested_features", [])
        state["questions"] = update.get("questions", [])

        self._save_state(state)
        return state

    # ---------------- PROMPT ----------------

    def _build_prompt(self, state, user_message):
        return f"""
You are an expert AI Product Manager and Software Architect.

Your job:
- Talk to the user
- Ask clarifying questions
- Suggest features with clear reasons
- Maintain a human-readable plan
- DO NOT approve unless user explicitly confirms

CURRENT STATE:
{json.dumps(state, indent=2)}

USER MESSAGE:
{user_message}

OUTPUT RULES (STRICT):
- Output ONLY valid JSON
- Do NOT include explanations outside JSON
- Do NOT finalize or approve unless user intent is explicit
- Always include:
  - status
  - current_plan
  - suggested_features
  - questions

JSON FORMAT:
{{
  "status": "draft or awaiting_confirmation",
  "current_plan": {{
    "app_type": "...",
    "pages": [...],
    "ai_features": [...]
  }},
  "suggested_features": [
    {{
      "id": "...",
      "title": "...",
      "why": "..."
    }}
  ],
  "questions": ["..."]
}}
"""

    # ---------------- STATE ----------------

    def _load_state(self):
        if os.path.exists(DRAFT_STATE):
            with open(DRAFT_STATE) as f:
                return json.load(f)

        return {
            "status": "draft",
            "current_plan": {
                "app_type": None,
                "pages": [],
                "ai_features": []
            },
            "suggested_features": [],
            "questions": []
        }

    def _save_state(self, state):
        with open(DRAFT_STATE, "w") as f:
            json.dump(state, f, indent=2)


if __name__ == "__main__":
    agent = ChatSpecAgent()
    print(json.dumps(
        agent.run("I want a portfolio website"),
        indent=2
    ))

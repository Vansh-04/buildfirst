import os
import json
from google import genai


class LLMReasoner:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY not set")

        self.client = genai.Client(api_key=api_key)

    def explain(self, spec, data_profile, strategy):
        prompt = f"""
You are an AI system architect.

PROJECT SPEC:
{json.dumps(spec, indent=2)}

DATA PROFILE:
{json.dumps(data_profile, indent=2)}

SYSTEM DECISION:
{json.dumps(strategy, indent=2)}

Explain in JSON ONLY with keys:
why_ai, why_task, why_model, risks, confidence
"""

        response = self.client.models.generate_content(
            model="gemini-1.5-flash",
            contents=prompt
        )

        text = response.text.strip()

        # 🔐 HARD GUARANTEE: always return JSON
        try:
            parsed = json.loads(text)
            parsed["_llm_status"] = "ok"
            return parsed
        except Exception:
            return {
                "_llm_status": "invalid_json",
                "raw_response": text
            }

import json
import os
from google import genai
from fastapi.middleware.cors import CORSMiddleware


class BackendCodegenAgent:
    """
    Backend code generator.
    - Uses LLM ONCE if needed
    - Caches generated code
    - Falls back to deterministic FastAPI if LLM is unavailable
    """
    def _sanitize_python(self, code: str) -> str:
        lines = []
        for line in code.splitlines():
            if line.strip().startswith("```"):
                continue
            lines.append(line)
        return "\n".join(lines).strip()

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        self.client = None

        if api_key:
            self.client = genai.Client(api_key=api_key)

        self.model = "models/gemini-2.5-flash"

    # ---------------- PUBLIC ----------------

    def run(self, backend_plan_path, output_dir):
        os.makedirs(output_dir, exist_ok=True)

        app_path = os.path.join(output_dir, "app.py")
        req_path = os.path.join(output_dir, "requirements.txt")

        # ✅ CACHE: Do not regenerate if already exists
        if os.path.exists(app_path) and os.path.exists(req_path):
            print("ℹ️ Backend already generated, skipping codegen")
            return

        plan = self._load(backend_plan_path)

        try:
            if self.client:
                print("🧠 Generating backend with LLM")
                code = self._generate_app_code_llm(plan)
            else:
                raise RuntimeError("LLM not available")

        except Exception as e:
            print("⚠️ LLM unavailable or quota exceeded")
            print("ℹ️ Falling back to deterministic backend generator")
            code = self._generate_app_code_deterministic(plan)

        requirements = self._generate_requirements(plan)

        self._write(output_dir, "app.py", code)
        self._write(output_dir, "requirements.txt", requirements)
        self._write(
            output_dir,
            "README.md",
            "Run backend with:\n\nuvicorn app:app --reload\n"
        )

        print("✅ Backend code generated")

    # ---------------- LLM CODEGEN ----------------

    def _generate_app_code_llm(self, plan):
        prompt = f"""
You are a senior backend engineer.

Generate a COMPLETE FastAPI backend.

BACKEND PLAN:
{json.dumps(plan, indent=2)}

REQUIREMENTS:
- Use FastAPI
- Enable CORS (allow all origins)
- Implement ALL routes listed
- Add /health endpoint
- AI routes ONLY if ai.enabled == true
- If AI enabled, stub model loading (NO training)
- Clean, production-ready Python
- Single file: app.py
- NO explanations, ONLY Python code
"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt
        )

        code = response.text.strip()
        code = self._sanitize_python(code)

        if "FastAPI" not in code or "app =" not in code:
            raise RuntimeError("Invalid FastAPI code from LLM")

        return code

    # ---------------- FALLBACK (NO LLM) ----------------

    def _generate_app_code_deterministic(self, plan):
        routes = plan.get("routes", [])
        ai_enabled = plan.get("ai", {}).get("enabled", False)

        route_blocks = []

        for r in routes:
            fn_name = r["name"].replace("-", "_")
            path = r["path"]

            route_blocks.append(f"""
@app.get("{path}")
def {fn_name}():
    return {{"route": "{path}", "status": "ok"}}
""")

        ai_block = ""
        if ai_enabled:
            ai_block = """
@app.post("/predict")
def predict(data: dict):
    return {"message": "AI enabled (fallback mode), model not loaded"}
"""

        return f"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {{"status": "ok"}}

{''.join(route_blocks)}

{ai_block}
"""

    # ---------------- REQUIREMENTS ----------------

    def _generate_requirements(self, plan):
        reqs = [
            "fastapi",
            "uvicorn",
            "pydantic",
            "python-multipart"
        ]

        if plan.get("ai", {}).get("enabled"):
            reqs.extend(["numpy", "joblib"])

        return "\n".join(sorted(set(reqs)))

    # ---------------- IO ----------------

    def _write(self, base, name, content):
        with open(os.path.join(base, name), "w") as f:
            f.write(content.strip() + "\n")

    def _load(self, path):
        with open(path) as f:
            return json.load(f)


if __name__ == "__main__":
    import sys

    BackendCodegenAgent().run(
        backend_plan_path=sys.argv[1],
        output_dir=sys.argv[2]
    )

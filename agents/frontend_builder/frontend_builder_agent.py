import json
import os
import re
from google import genai


class FrontendBuilderAgent:
    """
    LLM-driven frontend builder.
    Generates a SINGLE-PAGE HTML website using anchor navigation.
    Output is written into the generated project folder.
    """

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("❌ GEMINI_API_KEY not set")

        self.client = genai.Client(api_key=api_key)
        self.model = "models/gemini-2.5-flash"

    # ---------------- PUBLIC ----------------

    def run(self, app_plan_path, output_root="generated_projects"):
        index_path = os.path.join(output_dir, "index.html")

        if os.path.exists(index_path):
          print("ℹ Frontend already generated, skipping")
          return
        plan = self._load(app_plan_path)

        project_slug = self._project_slug(plan)
        output_dir = os.path.join(
            output_root,
            project_slug,
            "frontend"
        )

        os.makedirs(output_dir, exist_ok=True)

        html = self._generate_html_with_retry(plan)

        self._write_html(html, output_dir)

        print(f"✅ Frontend generated at {output_dir}/index.html")

    # ---------------- CORE ----------------

    def _generate_html_with_retry(self, plan):
        prompt = f"""
You are a senior frontend engineer.

TASK:
Generate a COMPLETE, production-quality SINGLE-PAGE HTML website.

INPUT PLAN:
{json.dumps(plan, indent=2)}

ABSOLUTE RULES:
- Output ONLY valid HTML (no markdown, no explanations)
- MUST include <html>, <head>, <body> and closing tags
- Use semantic HTML (header, nav, main, section, footer)
- SINGLE PAGE ONLY
- Each page becomes: <section id="page_id">
- Navigation links MUST be anchor links: href="#page_id"
- DO NOT use /about, /blog, or file-based routing
- Visually distinct sections
- Clean, professional styling (inline CSS allowed)
- No JavaScript frameworks

FAIL CONDITIONS:
- Missing closing tags
- Multiple HTML documents
- Broken navigation
"""

        for attempt in range(3):
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            html = response.text.strip()

            if self._is_valid_html(html):
                return html

            print(f"⚠️ Invalid HTML (attempt {attempt + 1}/3), retrying...")

        raise RuntimeError("❌ Failed to generate valid HTML after 3 attempts")

    # ---------------- VALIDATION ----------------

    def _is_valid_html(self, html: str) -> bool:
        lower = html.lower()
        return (
            "<html" in lower
            and "</html>" in lower
            and "<body" in lower
            and "</body>" in lower
            and "<section" in lower
            and "href=\"#" in lower
        )

    # ---------------- HELPERS ----------------

    def _project_slug(self, plan):
        name = (
            plan.get("application", {})
            .get("name", "autodev_project")
        )
        return (
            name.lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

    def _write_html(self, html, output_dir):
        path = os.path.join(output_dir, "index.html")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)

    def _load(self, path):
        with open(path) as f:
            return json.load(f)


if __name__ == "__main__":
    import sys

    FrontendBuilderAgent().run(
        app_plan_path=sys.argv[1]
    )

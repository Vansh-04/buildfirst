import json
import os


class BackendBuilderAgent:
    """
    Backend PLANNER.
    Accepts application_plan_v1.json (normalized).
    Writes backend_plan.json.
    """

    def run(self, app_plan_path, strategy_path, output_root="generated_projects"):
        app_plan = self._load(app_plan_path)
        strategy = self._load(strategy_path)

        # -------- NORMALIZE APPLICATION --------
        application = app_plan.get("application")
        if not application:
            # Fallback for safety
            application = {
                "name": app_plan.get("app_name", "autodev_project"),
                "type": "website"
            }

        project_slug = self._slug(application["name"])

        backend_dir = os.path.join(
            output_root,
            project_slug,
            "backend"
        )
        os.makedirs(backend_dir, exist_ok=True)

        backend_plan = self._build_backend_plan(
            application=application,
            pages=app_plan.get("pages", []),
            ai_widgets=app_plan.get("ai_widgets", {}),
            strategy=strategy
        )

        path = os.path.join(backend_dir, "backend_plan.json")
        with open(path, "w") as f:
            json.dump(backend_plan, f, indent=2)

        print(f"✅ backend_plan.json created at {path}")

    # ---------------- CORE ----------------

    def _build_backend_plan(self, application, pages, ai_widgets, strategy):
        routes = []

        for page in pages:
            routes.append({
                "path": page["route"],
                "method": "GET",
                "auth_required": page.get("requires_auth", False),
                "purpose": page["title"]
            })

        routes.append({
            "path": "/health",
            "method": "GET",
            "auth_required": False,
            "purpose": "Health check"
        })

        if strategy.get("ai_required"):
            routes.append({
                "path": "/predict",
                "method": "POST",
                "auth_required": False,
                "purpose": "AI inference"
            })

        return {
            "project": application,
            "stack": {
                "framework": "fastapi",
                "language": "python"
            },
            "ai": {
                "enabled": strategy.get("ai_required", False),
                "paradigm": strategy.get("learning_paradigm")
            },
            "routes": routes,
            "artifacts": {
                "model": "model.pkl" if strategy.get("ai_required") else None,
                "preprocessor": "preprocessor.pkl" if strategy.get("ai_required") else None
            }
        }

    # ---------------- HELPERS ----------------

    def _slug(self, name):
        return (
            name.lower()
            .replace(" ", "_")
            .replace("-", "_")
        )

    def _load(self, path):
        with open(path) as f:
            return json.load(f)


if __name__ == "__main__":
    import sys

    BackendBuilderAgent().run(
        app_plan_path=sys.argv[1],
        strategy_path=sys.argv[2]
    )

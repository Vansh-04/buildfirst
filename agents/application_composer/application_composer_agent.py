import json


class ApplicationComposerAgent:
    """
    Converts a human-friendly application spec
    into a machine-friendly application plan.
    """

    def run(self, app_spec_path, strategy_path=None):
        with open(app_spec_path) as f:
            app_spec = json.load(f)

        # -------- NORMALIZE TOP-LEVEL SPEC --------
        if "website" not in app_spec:
            app_spec = {
                "application": {
                    "name": app_spec.get("app_name", "AutoDev App"),
                    "type": "website"
                },
                "website": {
                    "pages": app_spec.get("pages", [])
                },
                "ai_features": app_spec.get("suggested_features", []),
                "env_configs": app_spec.get("env_configs", [])
            }

        website = app_spec.get("website", {})
        raw_pages = website.get("pages", [])
        raw_ai_features = app_spec.get("ai_features", [])

        # -------- NORMALIZE PAGES --------
        normalized_pages = []

        for idx, page in enumerate(raw_pages):
            name = page.get("name", f"Page {idx}")
            page_id = (
                page.get("id")
                or name.lower().replace(" ", "_").replace("/", "").replace("-", "_")
            )

            normalized_pages.append({
                "id": page_id,
                "title": name,
                "route": page.get("route", f"/{page_id}"),
                "description": page.get("description", ""),
                "components": page.get("components", []),
                "requires_auth": page.get("requires_auth", False)
            })

        # -------- NORMALIZE AI FEATURES --------
        ai_widgets = {}

        for idx, feature in enumerate(raw_ai_features):
            name = feature.get("name", f"AI Feature {idx}")
            feature_id = name.lower().replace(" ", "_")

            ai_widgets[feature_id] = {
                "label": name,
                "endpoint": "/predict",
                "input_source": "model_metadata",
                "output_style": "cards",
                "visibility": "public"
            }

        # -------- FINAL APPLICATION PLAN --------
        application_plan = {
            "application": app_spec.get("application", {}),
            "pages": normalized_pages,
            "ai_widgets": ai_widgets,
            "backend_routes": self._backend_routes(ai_widgets),
            "build_flags": {
                "ml_required": bool(ai_widgets),
                "backend_required": True,
                "frontend_required": True
            }
        }

        return application_plan

    def _backend_routes(self, ai_widgets):
        routes = ["/context"]
        if ai_widgets:
            routes.append("/predict")
        return routes


if __name__ == "__main__":
    import sys

    out = ApplicationComposerAgent().run(
        app_spec_path=sys.argv[1],
        strategy_path=sys.argv[2] if len(sys.argv) > 2 else None
    )

    with open("application_plan_v1.json", "w") as f:
        json.dump(out, f, indent=2)

    print("✅ application_plan_v1.json created")

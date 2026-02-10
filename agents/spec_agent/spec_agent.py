import json
from datetime import datetime

class SpecAgent:
    def __init__(self):
        self.spec = {
            "spec_version": "1.0",
            "project_identity": {},
            "functional_scope": {},
            "feature_set": {
                "core_features": [],
                "optional_features": []
            },
            "ui_spec": {},
            "system_constraints": {
                "no_hardcoding": True,
                "self_healing": True,
                "config_driven": True,
                "reproducible": True
            },
            "deployment_spec": {},
            "handoff": {}
        }

    def run(self):
        print("\n🧠 SpecAgent v1 — Project Specification\n")

        self.intent_discovery()
        self.feature_selection()
        self.ui_and_constraints()
        self.deployment_preferences()
        self.final_confirmation()

        self.write_spec()

    def intent_discovery(self):
        print("🔹 Phase 1: Intent Discovery")
        self.spec["project_identity"]["name"] = input("Project name: ")
        self.spec["project_identity"]["description"] = input("Short description: ")
        self.spec["project_identity"]["primary_goal"] = input("Primary goal: ")

        self.spec["functional_scope"]["application_type"] = self.choose(
            "Application type", ["web_app", "api", "dashboard", "cli"]
        )

        self.spec["functional_scope"]["problem_domain"] = self.choose(
            "Problem domain", ["ml", "dl", "data_app", "automation", "static_site"]
        )

    def feature_selection(self):
        print("\n🔹 Phase 2: Feature Selection")
        self.spec["feature_set"]["core_features"] = ["inference", "metrics_display"]

        optional = [
            "model_explainability",
            "confidence_scores",
            "user_feedback_loop",
            "prediction_history"
        ]

        for feat in optional:
            if input(f"Add '{feat}'? (y/n): ").lower() == "y":
                self.spec["feature_set"]["optional_features"].append(feat)

    def ui_and_constraints(self):
        print("\n🔹 Phase 3: UI & Constraints")
        self.spec["ui_spec"]["ui_style"] = self.choose(
            "UI style", ["chat", "dashboard", "hybrid", "none"]
        )
        pages = input("UI pages (comma separated): ")
        self.spec["ui_spec"]["pages"] = [p.strip() for p in pages.split(",") if p]
        self.spec["ui_spec"]["design_tone"] = self.choose(
            "Design tone", ["minimal", "modern", "developer"]
        )

    def deployment_preferences(self):
        print("\n🔹 Phase 4: Deployment")
        self.spec["deployment_spec"]["containerized"] = True
        self.spec["deployment_spec"]["local_run"] = True
        self.spec["deployment_spec"]["cloud_ready"] = True
        self.spec["deployment_spec"]["git_push_on_success"] = (
            input("Enable Git push? (y/n): ").lower() == "y"
        )

    def final_confirmation(self):
        print("\n🔹 Final Review\n")
        print(json.dumps(self.spec, indent=2))

        while True:
            choice = input("\nType GO to confirm or EXIT to stop: ")
            if choice == "GO":
                self.spec["handoff"] = {
                    "approved": True,
                    "approved_by_user": True,
                    "timestamp": datetime.utcnow().isoformat()
                }
                return
            elif choice == "EXIT":
                raise SystemExit("❌ Spec creation cancelled")

    def choose(self, label, options):
        print(f"\n{label}:")
        for i, opt in enumerate(options, 1):
            print(f"{i}. {opt}")
        return options[int(input("Choose option number: ")) - 1]

    def write_spec(self):
        with open("project_spec_v1.json", "w") as f:
            json.dump(self.spec, f, indent=2)
        print("\n✅ project_spec_v1.json created")


if __name__ == "__main__":
    SpecAgent().run()

import json

class DataAcquisitionAgent:
    def run(self, spec_path, data_profile_path):
        spec = self._load(spec_path)
        data = self._load(data_profile_path)

        # Only trigger for ML/DL projects with no data
        if data.get("data_present"):
            return self._emit_skip("Data already present")

        if spec["functional_scope"]["problem_domain"] not in ["ml", "dl"]:
            return self._emit_skip("Project does not require ML/DL")

        return self._ask_user()

    def _ask_user(self):
        print("\n📊 No dataset detected, but this is an ML project.")
        print("Choose how you want to proceed:\n")
        print("1. Upload a dataset")
        print("2. Connect external data source (API / URL)")
        print("3. Generate synthetic data (prototype only)")
        print("4. Skip ML for now (build app only)")

        choice = input("\nChoose option (1-4): ").strip()

        mapping = {
            "1": "upload",
            "2": "external_api",
            "3": "synthetic",
            "4": "defer"
        }

        strategy = mapping.get(choice)

        if not strategy:
            raise ValueError("Invalid choice")

        details = {}

        if strategy == "external_api":
            details["external_api_url"] = input("Enter API or data URL: ")
            details["expected_format"] = input("Expected format (csv/json): ")

        if strategy == "upload":
            details["expected_format"] = "csv"

        return {
            "data_strategy": strategy,
            "details": details,
            "user_confirmed": True
        }

    def _emit_skip(self, reason):
        return {
            "data_strategy": "skip",
            "reason": reason,
            "user_confirmed": True
        }

    def _load(self, path):
        with open(path) as f:
            return json.load(f)


if __name__ == "__main__":
    import sys

    spec = sys.argv[1]
    data_profile = sys.argv[2]

    agent = DataAcquisitionAgent()
    output = agent.run(spec, data_profile)

    with open("data_acquisition_plan_v1.json", "w") as f:
        json.dump(output, f, indent=2)

    print("✅ data_acquisition_plan_v1.json created")

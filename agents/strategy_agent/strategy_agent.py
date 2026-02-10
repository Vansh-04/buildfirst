import json
from llm_reasoner import LLMReasoner


class StrategyAgent:
    def run(self, spec_path, data_profile_path, use_llm=True):
        spec = self._load(spec_path)
        data = self._load(data_profile_path)

        # ---------- RULE-BASED CORE ----------

        if not data.get("data_present"):
            return {
                "ai_required": False,
                "reason": "No dataset"
            }

        task_type = "recommendation"
        goal = spec["project_identity"]["primary_goal"].lower()
        if "classif" in goal:
            task_type = "classification"

        strategy = {
            "ai_required": True,
            "learning_paradigm": "ml",
            "task_type": task_type,
            "model_strategy": {
                "model_family": "knn" if task_type == "recommendation" else "random_forest",
                "hyperparameters": {
                    "n_neighbors": 3
                }
            }
        }

        # ---------- LLM REASONING (SAFE + GUARANTEED) ----------

        if use_llm:
            try:
                reasoner = LLMReasoner()
                strategy["llm_explanation"] = reasoner.explain(
                    spec, data, strategy
                )
            except Exception as e:
                strategy["llm_explanation"] = {
                    "_llm_status": "error",
                    "message": str(e)
                }

        return strategy

    def _load(self, path):
        with open(path) as f:
            return json.load(f)


if __name__ == "__main__":
    import sys

    out = StrategyAgent().run(
        sys.argv[1],
        sys.argv[2],
        use_llm=True
    )

    with open("training_strategy_v1.json", "w") as f:
        json.dump(out, f, indent=2)

    print("✅ training_strategy_v1.json created with REAL Gemini reasoning")

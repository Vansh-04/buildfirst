import os
import json
import subprocess

def run(cmd):
    print("▶", " ".join(cmd))
    subprocess.run(cmd, check=True)

def write_status(status):
    with open("build_status.json", "w") as f:
        json.dump({"status": status}, f)

def main():
    print("🚀 AutoDev Orchestrator v2")
    write_status("STARTED")

    # 1. Strategy (optional, safe if non-AI)
    if os.path.exists("data_profile_v1.json"):
        run([
            "python",
            "agents/strategy_agent/strategy_agent.py",
            "project_spec_v1.json",
            "data_profile_v1.json"
        ])

    # 2. Train model if strategy says so
    if os.path.exists("training_strategy_v1.json"):
        run([
            "python",
            "agents/trainer_agent/trainer_agent.py",
            "training_strategy_v1.json",
            "data_profile_v1.json",
            "data/sample.csv"
        ])

    # 3. Compose application
    run([
        "python",
        "agents/application_composer/application_composer_agent.py",
        "application_spec_v1.json",
        "training_strategy_v1.json"
    ])

    # 4. Build backend PLAN (NO LLM)
    run([
        "python",
        "agents/backend_builder/backend_builder_agent.py",
        "application_plan_v1.json",
        "training_strategy_v1.json"
    ])

    # 5. Generate backend CODE (LLM)
    run([
        "python",
        "agents/backend_codegen/backend_codegen_agent.py",
        "generated_projects/portfolio_website_with_blog/backend/backend_plan.json",
        "generated_projects/portfolio_website_with_blog/backend"
    ])

    # 6. Generate frontend (LLM HTML)
    run([
        "python",
        "agents/frontend_builder/frontend_builder_agent.py",
        "application_plan_v1.json"
    ])

    write_status("DONE")
    print("✅ AutoDev build complete")

if __name__ == "__main__":
    main()

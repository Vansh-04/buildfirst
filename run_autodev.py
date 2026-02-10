import argparse
import os
import subprocess
from agents.self_healing.self_healing_agent import SelfHealingAgent

ROOT = os.getcwd()

def run(cmd):
    print("\n▶", " ".join(cmd))
    SelfHealingAgent().run_with_healing(cmd)

def file_exists(path):
    return os.path.exists(path)

def main(data_path=None):
    # 1. Spec MUST exist
    if not file_exists("project_spec_v1.json"):
        raise RuntimeError("project_spec_v1.json not found. Run SpecAgent first.")

    # 2. Data Inspector
    if data_path:
        run([
            "python",
            "agents/data_inspector/data_inspector.py",
            "project_spec_v1.json",
            data_path
        ])
    else:
        run([
            "python",
            "agents/data_inspector/data_inspector.py",
            "project_spec_v1.json"
        ])

    # 3. Strategy Agent
    run([
        "python",
        "agents/strategy_agent/strategy_agent.py",
        "project_spec_v1.json",
        "data_profile_v1.json"
    ])

    # 4. Train model (only if dataset exists)
    if data_path:
        run([
            "python",
            "agents/trainer_agent/trainer_agent.py",
            "training_strategy_v1.json",
            "data_profile_v1.json",
            data_path
        ])
    else:
        print("⚠️ No dataset provided. Skipping training.")

    # 5. Backend
    run([
        "python",
        "agents/backend_builder/backend_builder_agent.py",
        "project_spec_v1.json",
        "training_strategy_v1.json",
        "data_profile_v1.json"
    ])

    # 6. Frontend
    run([
        "python",
        "agents/frontend_builder/frontend_builder_agent.py",
        "project_spec_v1.json",
        "training_strategy_v1.json"
    ])

    print("\n✅ AutoDev v1 pipeline complete")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", help="Path to dataset (optional)")
    args = parser.parse_args()

    main(args.data)

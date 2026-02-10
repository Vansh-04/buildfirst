{
  "spec_version": "1.0",

  "project_identity": {
    "name": "string",
    "description": "string",
    "primary_goal": "string"
  },

  "functional_scope": {
    "application_type": "web_app | api | dashboard | cli",
    "problem_domain": "ml | dl | data_app | automation",
    "user_interactions": ["upload", "chat", "form", "api_call"],
    "expected_outputs": ["prediction", "confidence", "explanations"]
  },

  "feature_set": {
    "core_features": [
      "inference",
      "metrics_display"
    ],
    "optional_features": [
      "model_explainability",
      "confidence_scores",
      "user_feedback_loop"
    ]
  },

  "ui_spec": {
    "ui_style": "chat | dashboard | hybrid | none",
    "pages": [],
    "design_tone": "minimal | modern | developer"
  },

  "system_constraints": {
    "no_hardcoding": true,
    "self_healing": true,
    "config_driven": true,
    "reproducible": true
  },

  "deployment_spec": {
    "containerized": true,
    "local_run": true,
    "cloud_ready": true,
    "git_push_on_success": true
  },

  "handoff": {
    "approved": true,
    "approved_by_user": true,
    "timestamp": "ISO_8601"
  }
}

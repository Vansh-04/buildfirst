import json

class LLMReasoner:
    def reason(self, spec, data_profile):
        """
        This does NOT decide.
        It only SUGGESTS.
        """

        return {
            "suggested_task": "recommendation",
            "suggested_models": ["knn", "cosine_similarity"],
            "notes": "Dataset appears similarity-based with no clear target"
        }

import json
import joblib
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

class TrainerAgent:
    def run(self, strategy_path, data_profile_path, dataset_path):
        strategy = self._load(strategy_path)
        data = self._load(data_profile_path)

        if not strategy.get("ai_required"):
            print("⚠️ AI not required")
            return

        df = pd.read_csv(dataset_path)
        X = df.select_dtypes(include="number")

# Drop likely index / ID columns automatically
        X = X.loc[:, ~X.columns.str.contains("unnamed|id", case=False)]

        if X.empty:
            raise ValueError("No numeric columns found in dataset")

        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)

        model = NearestNeighbors(
            n_neighbors=strategy["model_strategy"]["hyperparameters"]["n_neighbors"]
        )
        model.fit(X_scaled)

        # Save model artifacts
        joblib.dump(model, "model.pkl")
        joblib.dump(scaler, "preprocessor.pkl")

        # Save metadata (CRITICAL)
        metadata = {
            "feature_count": X.shape[1],
            "feature_names": list(X.columns)
        }

        with open("model_metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        print("✅ Model trained")
        print("ℹ️ Feature count:", X.shape[1])

    def _load(self, path):
        with open(path) as f:
            return json.load(f)

if __name__ == "__main__":
    import sys
    TrainerAgent().run(sys.argv[1], sys.argv[2], sys.argv[3])

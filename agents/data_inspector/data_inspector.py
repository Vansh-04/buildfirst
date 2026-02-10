import os
import json
import pandas as pd

class DataInspectorAgent:
    def run(self, spec_path, dataset_path=None):

        if not dataset_path or not os.path.exists(dataset_path):
            return self.emit_no_data()

        ext = os.path.splitext(dataset_path)[1].lower()

        if ext == ".csv":
            return self.inspect_csv(dataset_path)
        elif ext in [".jpg", ".png", ".jpeg"]:
            return self.emit_simple("image", dataset_path)
        elif ext == ".txt":
            return self.emit_simple("text", dataset_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

    def inspect_csv(self, path):
        df = pd.read_csv(path)
        rows, cols = df.shape
        size_mb = os.path.getsize(path) / (1024 * 1024)

        target = self.detect_target(df)

        return {
            "data_present": True,
            "modality": "tabular",
            "rows": rows,
            "columns": cols,
            "column_names": list(df.columns),
            "target_detected": target is not None,
            "target_column": target,
            "size_mb": round(size_mb, 2)
        }

    def detect_target(self, df):
        for col in ["label", "target", "class", "y"]:
            if col in df.columns:
                return col
        if df[df.columns[-1]].dtype == "object":
            return df.columns[-1]
        return None

    def emit_simple(self, modality, path):
        size_mb = os.path.getsize(path) / (1024 * 1024)
        return {
            "data_present": True,
            "modality": modality,
            "size_mb": round(size_mb, 2)
        }

    def emit_no_data(self):
        return {
            "data_present": False,
            "reason": "no_dataset_provided",
            "project_nature": "non_ml_or_static"
        }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(
            "\n❌ Missing arguments.\n\n"
            "Usage:\n"
            "  python data_inspector.py <project_spec_v1.json> [dataset_path]\n\n"
            "Examples:\n"
            "  python data_inspector.py project_spec_v1.json\n"
            "  python data_inspector.py project_spec_v1.json data.csv\n"
        )
        sys.exit(1)

    spec = sys.argv[1]
    data = sys.argv[2] if len(sys.argv) > 2 else None

    output = DataInspectorAgent().run(spec, data)

    with open("data_profile_v1.json", "w") as f:
        json.dump(output, f, indent=2)

    print("✅ data_profile_v1.json created")

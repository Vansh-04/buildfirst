import joblib
import torch

def load_model(model_path, paradigm):
    if paradigm == "ml":
        return joblib.load(model_path)
    elif paradigm == "dl":
        model = torch.load(model_path, map_location="cpu")
        return model
    return None

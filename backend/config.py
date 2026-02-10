PROJECT_NAME = "recipe genrator"
AI_REQUIRED = True
LEARNING_PARADIGM = "ml"
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")
PREPROCESSOR_PATH = os.path.join(BASE_DIR, "preprocessor.pkl")

MODALITY = "tabular"

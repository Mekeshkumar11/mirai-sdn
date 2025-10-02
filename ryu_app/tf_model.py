import os
import numpy as np
import tensorflow as tf
from tensorflow.keras.models import load_model
import yaml

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
CONFIG_PATH = os.path.join(BASE_DIR, 'configs', 'model_config.yaml')

with open(CONFIG_PATH) as f:
    CFG = yaml.safe_load(f)

MODEL_REL = CFG.get('model_path', '../model/model.h5')
MODEL_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), MODEL_REL))

_model = None

def load_tf_model():
    global _model
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError(f"Model file not found at: {MODEL_PATH}")
        _model = load_model(MODEL_PATH)
    return _model

def predict_proba(feature_vector):
    """
    feature_vector: numpy array shape (n_features,) or (1, n_features)
    returns: numpy array of probabilities (n_classes,)
    """
    m = load_tf_model()
    x = np.array(feature_vector, dtype=np.float32)
    if x.ndim == 1:
        x = x.reshape(1, -1)
    preds = m.predict(x, verbose=0)  # model should output logits or probabilities
    # If model outputs logits, convert to softmax
    if preds.ndim == 2 and preds.shape[1] > 1:
        # assume already probabilities, but guard: normalize
        probs = preds / (preds.sum(axis=1, keepdims=True) + 1e-12)
        return probs[0]
    else:
        # binary single-output model -> map to two-class probs
        p = float(preds.reshape(-1)[0])
        return np.array([1.0 - p, p], dtype=np.float32)

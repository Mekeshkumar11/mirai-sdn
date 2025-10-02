import os
import json
import numpy as np

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
SCALER_PATH = os.path.join(BASE_DIR, 'configs', 'scaler_params.json')

def load_scaler():
    if not os.path.exists(SCALER_PATH):
        # fallback: identity
        return {'method': 'none'}
    with open(SCALER_PATH) as f:
        cfg = json.load(f)
    return cfg

SCALER = load_scaler()

def preprocess_vector(vec):
    """
    vec: numpy array (n_features,)
    returns normalized numpy array (same shape)
    """
    if SCALER.get('method') == 'standard':
        mean = np.array(SCALER.get('mean', []), dtype=np.float32)
        std = np.array(SCALER.get('std', []), dtype=np.float32)
        if mean.size != vec.size or std.size != vec.size:
            # fallback
            return vec.astype(np.float32)
        std[std == 0] = 1.0
        return (vec - mean) / std
    elif SCALER.get('method') == 'minmax':
        vmin = np.array(SCALER.get('min', []), dtype=np.float32)
        vmax = np.array(SCALER.get('max', []), dtype=np.float32)
        if vmin.size != vec.size or vmax.size != vec.size:
            return vec.astype(np.float32)
        denom = (vmax - vmin)
        denom[denom == 0] = 1.0
        return (vec - vmin) / denom
    else:
        return vec.astype(np.float32)

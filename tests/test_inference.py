import numpy as np
from ryu_app import tf_model, feature_extractor

def test_inference():
    try:
        m = tf_model.load_tf_model()
    except Exception as e:
        print("Model load failed:", e)
        return
    dummy_vec = np.zeros((len(feature_extractor.FEATURE_NAMES),), dtype=np.float32)
    probs = tf_model.predict_proba(dummy_vec)
    print("Predicted probs:", probs)

if __name__ == "__main__":
    test_inference()

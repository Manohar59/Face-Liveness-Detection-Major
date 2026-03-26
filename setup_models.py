"""
Download and extract dlib face landmark model required for face detection.
Run this once before using the app.
"""
import os
import urllib.request
import bz2
import sys

MODEL_URL = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
MODEL_DIR = "models"
MODEL_PATH = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat")

def setup_models():
    os.makedirs(MODEL_DIR, exist_ok=True)
    
    if os.path.exists(MODEL_PATH):
        print(f"Model already exists at {MODEL_PATH}")
        return True

    bz2_path = os.path.join(MODEL_DIR, "shape_predictor_68_face_landmarks.dat.bz2")
    
    print("Downloading shape_predictor_68_face_landmarks.dat.bz2...")
    try:
        urllib.request.urlretrieve(MODEL_URL, bz2_path)
    except Exception as e:
        print(f"Download failed: {e}")
        print("\nManual download:")
        print(f"  1. Visit: {MODEL_URL}")
        print("  2. Extract the .bz2 file")
        print(f"  3. Place shape_predictor_68_face_landmarks.dat in {MODEL_DIR}/")
        return False

    print("Extracting...")
    try:
        with bz2.open(bz2_path, "rb") as f_in:
            with open(MODEL_PATH, "wb") as f_out:
                f_out.write(f_in.read())
        os.remove(bz2_path)
        print(f"Model saved to {MODEL_PATH}")
        return True
    except Exception as e:
        print(f"Extraction failed: {e}")
        return False

if __name__ == "__main__":
    success = setup_models()
    sys.exit(0 if success else 1)

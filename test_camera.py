"""
Simple camera diagnostics script.
Run:
    python test_camera.py
It will print which camera indices/backends open successfully.
"""
import cv2


def main():
    indices = [0, 1, 2, 3]
    # Some OpenCV builds may not have all backends, so we guard access.
    possible_backends = []
    for attr in ["CAP_DSHOW", "CAP_MSMF", "CAP_ANY"]:
        if hasattr(cv2, attr):
            possible_backends.append(getattr(cv2, attr))

    if not possible_backends:
        possible_backends = [0]

    print("Testing cameras...\n")
    for idx in indices:
        for backend in possible_backends:
            print(f"Trying index {idx}, backend {backend}...", end=" ")
            try:
                cap = cv2.VideoCapture(idx, backend)
            except Exception as e:
                print(f"EXCEPTION: {e}")
                continue

            if cap is not None and cap.isOpened():
                print("OK (opened)")
                cap.release()
            else:
                print("failed")


if __name__ == "__main__":
    main()


"""
sign_recognizer.py
Uses MediaPipe landmarks (proven to work) + SVM
Supports 1 AND 2 hands
"""

import cv2
import numpy as np
import mediapipe as mp
import pickle
import os

class SignRecognizer:
    def __init__(self, mode="ISL"):
        self.mode = mode
        self.model = None
        self.label_encoder = None
        self.is_loaded = False
        self.model_paths = {
            "ISL": ("models/isl_svm_model.pkl", "models/isl_label_encoder.pkl"),
            "ASL": ("models/asl_svm_model.pkl", "models/asl_label_encoder.pkl"),
        }
        self.mp_hands = mp.solutions.hands
        self.mp_draw  = mp.solutions.drawing_utils
        self.hands    = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=2,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        self.load_model(mode)

    def load_model(self, mode="ISL"):
        self.mode = mode
        mp_path, ep_path = self.model_paths.get(mode, self.model_paths["ISL"])
        if os.path.exists(mp_path) and os.path.exists(ep_path):
            try:
                with open(mp_path, 'rb') as f:
                    self.model = pickle.load(f)
                with open(ep_path, 'rb') as f:
                    self.label_encoder = pickle.load(f)
                self.is_loaded = True
                print(f"{mode} model loaded!")
            except Exception as e:
                print(f"Error loading {mode}: {e}")
                self.is_loaded = False
        else:
            print(f"{mode} model not found. Run train_isl_model.py first.")
            self.is_loaded = False

    def switch_mode(self, mode):
        if mode != self.mode:
            self.load_model(mode)

    def extract_landmarks(self, frame):
        """Extract landmarks from frame - supports 2 hands"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results   = self.hands.process(frame_rgb)

        if not results.multi_hand_landmarks:
            return None, results

        landmarks = []
        # Use up to 2 hands - pad with zeros if only 1 hand
        for hand_idx in range(min(2, len(results.multi_hand_landmarks))):
            hand_lm = results.multi_hand_landmarks[hand_idx]
            coords  = [(lm.x, lm.y, lm.z) for lm in hand_lm.landmark]
            # Normalize relative to wrist
            wx, wy, wz = coords[0]
            for x, y, z in coords:
                landmarks.extend([x - wx, y - wy, z - wz])

        # If only 1 hand detected, pad with zeros for 2nd hand
        if len(results.multi_hand_landmarks) == 1:
            landmarks.extend([0.0] * 63)

        return landmarks, results

    def predict(self, frame):
        """Predict sign - works with 1 or 2 hands"""
        if not self.is_loaded:
            return None, 0.0

        landmarks, results = self.extract_landmarks(frame)
        if landmarks is None:
            return None, 0.0

        try:
            arr  = np.array(landmarks).reshape(1, -1)
            pred = self.model.predict(arr)[0]
            prob = self.model.predict_proba(arr)[0]
            conf = max(prob) * 100
            letter = self.label_encoder.inverse_transform([pred])[0]
            return letter, conf
        except Exception as e:
            print(f"Prediction error: {e}")
            return None, 0.0

    def draw_landmarks(self, frame, results):
        """Draw landmarks for all detected hands"""
        if results and results.multi_hand_landmarks:
            for hand_lm in results.multi_hand_landmarks:
                self.mp_draw.draw_landmarks(
                    frame, hand_lm,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_draw.DrawingSpec(color=(0,255,0), thickness=2),
                    self.mp_draw.DrawingSpec(color=(0,0,255), thickness=2)
                )
        return frame

    def close(self):
        self.hands.close()
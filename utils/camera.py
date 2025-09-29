import cv2 
import math
import numpy as np
from collections import deque
import time

class PeekingDetector:
    def __init__(self):
        # Camera initialization with optimized settings
        self.cap = self._initialize_camera()
        self.detector = self._initialize_detector()
        
        # Detection parameters
        self.detection_window = deque(maxlen=5)
        self.required_confidence = 0.7
        self.last_valid_result = None
        self.last_processed_time = 0
        self.processing_interval = 0.033  # Target ~30 FPS processing
        
        # Performance tracking
        self.frame_count = 0
        self.start_time = time.time()

    def _initialize_camera(self):
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            raise RuntimeError("Could not open camera")
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 60)
        cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)  # Reduce latency
        return cap

    def _initialize_detector(self):
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml")
        return {'face': face_cascade, 'eye': eye_cascade}

    def release(self):
        """Release camera safely"""
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
            fps = self.frame_count / (time.time() - self.start_time)
            print(f"Camera released. Average FPS: {fps:.1f}")

    def __del__(self):
        self.release()

    def get_face_orientation(self, face_rect, eye_centers):
        x, y, w, h = face_rect
        eyes_center_y = (eye_centers[0][1] + eye_centers[1][1]) / 2
        vertical_ratio = (eyes_center_y - y) / h
        vertical_angle = (vertical_ratio - 0.35) * 100
        dx = eye_centers[1][0] - eye_centers[0][0]
        dy = eye_centers[1][1] - eye_centers[0][1]
        horizontal_angle = math.degrees(math.atan2(dy, dx))
        return vertical_angle, horizontal_angle

    def analyze_frame(self, frame):
        result = {
            'frame': frame.copy(),
            'face_detected': False,
            'peeking': False,
            'message': "No face detected",
            'vert_angle': 0,
            'horiz_angle': 0,
            'landmarks': [],
            'is_black': False
        }
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.equalizeHist(gray)
        if np.mean(gray) < 30:
            result['message'] = "Low lighting"
            result['is_black'] = True
            return result
        faces = self.detector['face'].detectMultiScale(gray, scaleFactor=1.05,
                                                       minNeighbors=6, minSize=(80, 80),
                                                       flags=cv2.CASCADE_SCALE_IMAGE)
        if len(faces) == 0:
            return result
        x, y, w, h = max(faces, key=lambda f: f[2]*f[3])
        result['face_detected'] = True
        cv2.rectangle(result['frame'], (x, y), (x+w, y+h), (0, 255, 0), 2)
        roi_gray = gray[y:y+h, x:x+w]
        eyes = self.detector['eye'].detectMultiScale(roi_gray, scaleFactor=1.05,
                                                     minNeighbors=5, minSize=(30, 30))
        if len(eyes) < 2:
            result['message'] = "Eyes not detected"
            return result
        eyes = sorted(eyes, key=lambda e: e[0])[:2]
        eye_centers = [(x + ex + ew//2, y + ey + eh//2) for ex, ey, ew, eh in eyes]
        result['landmarks'] = eye_centers
        for center in eye_centers:
            cv2.circle(result['frame'], center, 5, (0, 0, 255), -1)
        cv2.line(result['frame'], eye_centers[0], eye_centers[1], (255, 0, 0), 2)
        vert_angle, horiz_angle = self.get_face_orientation((x, y, w, h), eye_centers)
        result['vert_angle'] = vert_angle
        result['horiz_angle'] = horiz_angle
        eye_y_mean = (eye_centers[0][1] + eye_centers[1][1]) / 2
        eye_ratio = (eye_y_mean - y) / h
        if abs(vert_angle) > 40 or abs(horiz_angle) > 25:
            result['message'] = f"Head turned ({vert_angle:.1f}°, {horiz_angle:.1f}°)"
        elif eye_ratio < 0.25:
            result['message'] = "Looking up"
        elif eye_ratio > 0.6:
            result['message'] = "Looking down"
        else:
            result['peeking'] = True
            result['message'] = "Looking at screen"
        return result

    def is_user_peeking(self):
        self.frame_count += 1
        ret, frame = self.cap.read()
        if not ret:
            return False, self._create_error_result("Camera error")
        current_time = time.time()
        if current_time - self.last_processed_time < self.processing_interval:
            if self.last_valid_result:
                result = self.last_valid_result.copy()
                result['frame'] = frame
                result['message'] = "Throttling"
                return False, result
            return False, self._create_default_result(frame)
        self.last_processed_time = current_time
        analysis = self.analyze_frame(frame)
        self.detection_window.append(analysis['peeking'])
        if analysis['face_detected']:
            self.last_valid_result = analysis
        confidence = (sum(self.detection_window) / len(self.detection_window)
                      if self.detection_window else 0)
        return confidence >= self.required_confidence, analysis

    def _create_default_result(self, frame):
        return {'frame': frame, 'face_detected': False, 'peeking': False,
                'message': "Ready", 'vert_angle': 0, 'horiz_angle': 0,
                'landmarks': []}

    def _create_error_result(self, message):
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, message, (50, 240),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
        return {'frame': error_frame, 'face_detected': False, 'peeking': False,
                'message': message, 'vert_angle': 0, 'horiz_angle': 0,
                'landmarks': []}

# Global detector instance
detector = None

def get_detector():
    global detector
    if detector is None:
        try:
            detector = PeekingDetector()
        except Exception as e:
            print(f"Camera init failed: {str(e)}")
            detector = None
    return detector

def release_detector():
    """Explicitly release camera when done"""
    global detector
    if detector:
        detector.release()
        detector = None

def is_user_peeking():
    det = get_detector()
    if det is None:
        return False, {'frame': np.zeros((480, 640, 3), dtype=np.uint8),
                       'face_detected': False, 'peeking': False,
                       'message': "Camera unavailable",
                       'vert_angle': 0, 'horiz_angle': 0,
                       'landmarks': []}
    try:
        return det.is_user_peeking()
    except Exception as e:
        print(f"[Camera] Critical error: {str(e)}")
        return False, {'frame': np.zeros((480, 640, 3), dtype=np.uint8),
                       'face_detected': False, 'peeking': False,
                       'message': "Detection error",
                       'vert_angle': 0, 'horiz_angle': 0,
                       'landmarks': []}

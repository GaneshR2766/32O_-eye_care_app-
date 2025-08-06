# camera.py (with visual markers restored)
import cv2
import math
import numpy as np
from collections import deque

class PeekingDetector:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        if not self.cap.isOpened():
            raise RuntimeError("Could not open camera")
        
        # Configure camera
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 15)
        
        # Detection parameters
        self.detection_window = deque(maxlen=10)
        self.required_confidence = 0.7
        self.last_valid_face = None
        
        # Load classifiers
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
        self.eye_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_eye.xml")
        
    def __del__(self):
        if hasattr(self, 'cap') and self.cap.isOpened():
            self.cap.release()
    
    def get_face_orientation(self, face_rect, eye_centers):
        """More robust orientation calculation"""
        x, y, w, h = face_rect
        
        # Calculate vertical angle (pitch)
        eyes_center_y = (eye_centers[0][1] + eye_centers[1][1]) / 2
        chin_y = y + h
        vertical_ratio = (eyes_center_y - y) / (chin_y - y)
        vertical_angle = (vertical_ratio - 0.4) * 90
        
        # Calculate horizontal angle (yaw)
        dx = eye_centers[1][0] - eye_centers[0][0]
        dy = eye_centers[1][1] - eye_centers[0][1]
        horizontal_angle = math.degrees(math.atan2(dy, dx))
        
        return vertical_angle, horizontal_angle
    
    def analyze_frame(self, frame):
        """Improved frame analysis with better tilt handling"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        height, width = frame.shape[:2]
        
        result = {
            'frame': frame,
            'face_detected': False,
            'peeking': False,
            'message': "No face detected",
            'vert_angle': 0,
            'horiz_angle': 0,
            'eye_ratio': 0
        }
        
        # Check if frame is too dark
        if np.mean(gray) < 30:
            result['message'] = "Frame too dark"
            return result
            
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(100, 100))
        if len(faces) == 0:
            return result
            
        x, y, w, h = faces[0]  # Use largest face
        result['face_detected'] = True
        
        # Draw green rectangle around face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        
        # Eye detection with ROI
        roi_gray = gray[y:y+h, x:x+w]
        eyes = self.eye_cascade.detectMultiScale(roi_gray, 1.1, 3, minSize=(30, 30))
        
        if len(eyes) < 2:
            result['message'] = "Not enough eyes detected"
            return result
            
        # Sort eyes by x-position (left to right)
        eyes = sorted(eyes, key=lambda e: e[0])
        eye_centers = [(x + ex + ew//2, y + ey + eh//2) for ex, ey, ew, eh in eyes[:2]]
        
        # Draw red dots for eyes
        for (ex, ey) in eye_centers:
            cv2.circle(frame, (ex, ey), 5, (0, 0, 255), -1)
        
        # Draw blue line between eyes
        cv2.line(frame, eye_centers[0], eye_centers[1], (255, 0, 0), 2)
        
        # Get face orientation
        vert_angle, horiz_angle = self.get_face_orientation((x,y,w,h), eye_centers)
        result['vert_angle'] = vert_angle
        result['horiz_angle'] = horiz_angle
        
        # Eye position analysis
        eye_y_mean = (eye_centers[0][1] + eye_centers[1][1]) / 2
        eye_position_ratio = (eye_y_mean - y) / h
        result['eye_ratio'] = eye_position_ratio
        
        # Improved tilt detection rules
        if abs(vert_angle) > 45:
            result['message'] = f"Head tilted {vert_angle:.1f}°"
            return result
            
        if abs(horiz_angle) > 30:
            result['message'] = f"Head turned {horiz_angle:.1f}°"
            return result
            
        # Dynamic position thresholds
        if vert_angle > 15:  # Looking up
            upper_threshold = 0.4 + (vert_angle / 100)
            lower_threshold = 0.2
        elif vert_angle < -15:  # Looking down
            upper_threshold = 0.6
            lower_threshold = 0.4 + (vert_angle / 100)
        else:  # Neutral position
            upper_threshold = 0.5
            lower_threshold = 0.3
            
        if eye_position_ratio < lower_threshold:
            result['message'] = f"Looking up (eyes: {eye_position_ratio:.2f})"
            return result
            
        if eye_position_ratio > upper_threshold:
            result['message'] = f"Looking down (eyes: {eye_position_ratio:.2f})"
            return result
            
        # Only consider peeking when:
        # - Head is relatively straight (-15° to +15° tilt)
        # - Eyes are within neutral position
        result['peeking'] = True
        result['message'] = f"Potential peeking (eyes: {eye_position_ratio:.2f})"
        return result
    
    def is_user_peeking(self):
        """Smart detection with multiple frames"""
        try:
            analysis_results = []
            for _ in range(5):
                ret, frame = self.cap.read()
                if not ret:
                    print("[Camera] ❌ Frame capture failed")
                    # Create black frame with error message
                    error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
                    cv2.putText(error_frame, "Camera Error", (50, 240), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                    return False, {
                        'frame': error_frame, 
                        'face_detected': False, 
                        'message': "Camera error"
                    }
                
                analysis = self.analyze_frame(frame)
                self.detection_window.append(analysis['peeking'])
                analysis_results.append(analysis)
            
            confidence = sum(self.detection_window) / len(self.detection_window)
            if confidence >= self.required_confidence:
                return True, analysis_results[-1]
            return False, analysis_results[-1]
            
        except Exception as e:
            print(f"[Camera] ⚠️ Error: {str(e)}")
            # Create black frame with error message
            error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            cv2.putText(error_frame, f"Error: {str(e)}", (50, 240), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            return False, {
                'frame': error_frame, 
                'face_detected': False, 
                'message': f"Error: {str(e)}"
            }

# Initialize detector once at module level
try:
    peeking_detector = PeekingDetector()
except RuntimeError as e:
    print(f"Failed to initialize camera: {e}")
    peeking_detector = None

def is_user_peeking():
    """Public interface for peeking detection"""
    if peeking_detector is None:
        # Create black frame with error message
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, "Camera Not Available", (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return False, {
            'frame': error_frame, 
            'face_detected': False, 
            'message': "Camera not available"
        }
    
    try:
        return peeking_detector.is_user_peeking()
    except Exception as e:
        print(f"[Camera] Critical error: {str(e)}")
        # Create black frame with error message
        error_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        cv2.putText(error_frame, "Detection Failed", (50, 240), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        return False, {
            'frame': error_frame, 
            'face_detected': False, 
            'message': "Detection failed"
        }
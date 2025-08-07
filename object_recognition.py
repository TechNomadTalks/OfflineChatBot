# vision/object_recognition.py

import cv2
from ultralytics import YOLO
import concurrent.futures
from typing import List, Dict
import time

class ObjectRecognizer:
    def __init__(self):
        self.model = None
        self.cap = None
        self._init_model()
        
    def _init_model(self):
        """Lazy load YOLOv8 model for faster startup."""
        if self.model is None:
            self.model = YOLO('yolov8n.pt')
    
    def recognize_objects(self) -> List[Dict]:
        """Perform object recognition using webcam with timeout and threading."""
        start_time = time.time()
        try:
            self.cap = cv2.VideoCapture(0)
            if not self.cap.isOpened():
                return [{"error": "Camera initialization failed"}]
            
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
            
            objects_detected = set()
            last_detection_time = time.time()
            
            while (time.time() - last_detection_time) < 5:
                ret, frame = self.cap.read()
                if not ret:
                    continue
                
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(self.model, frame)
                    try:
                        results = future.result(timeout=1.0)
                        detected = results[0]
                        current_objects = {self.model.names[int(cls)] for cls in detected.boxes.cls}
                        if current_objects:
                            objects_detected.update(current_objects)
                            last_detection_time = time.time()
                        
                        cv2.imshow("Object Recognition", detected.plot())
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                    except concurrent.futures.TimeoutError:
                        continue
            
            return [{
                "objects": list(objects_detected),
                "processing_time": time.time() - start_time
            }] if objects_detected else [{"message": "No objects detected"}]
        
        except Exception as e:
            return [{"error": f"Recognition failed: {str(e)}"}]
        
        finally:
            if self.cap and self.cap.isOpened():
                self.cap.release()
            cv2.destroyAllWindows()

object_recognizer = ObjectRecognizer()

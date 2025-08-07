import os
import cv2
import time
from ultralytics import YOLO
from ai_modules.online_ai import get_online_response

# Load YOLOv8x model (you can replace with a custom model path)
MODEL_PATH = os.path.join(os.path.dirname(__file__), "yolov8x.pt")

class ObjectRecognizer:
    def __init__(self):
        self.model = None
        self.load_model()

    def load_model(self):
        try:
            self.model = YOLO(MODEL_PATH)
        except Exception as e:
            print(f"❌ Failed to load YOLO model: {e}")
            self.model = None

    def recognize_objects(self, image_path=None, online_mode=False):
        # If scanning from file
        if image_path:
            image = cv2.imread(image_path)
            if image is None:
                return [f"❌ Failed to read image at {image_path}"]
            return self._process_image(image, online_mode)

        # If scanning from webcam
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return ["❌ Camera not available"]

        print("🔍 Press 'q' to stop scanning.")
        results = []

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                cv2.imshow("Scanning... (press 'q' to quit)", frame)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    results = self._process_image(frame, online_mode)
                    break
        finally:
            cap.release()
            cv2.destroyAllWindows()

        return results

    def _process_image(self, image, online_mode=False):
        if self.model is None:
            return ["❌ Model not loaded"]

        results = self.model(image)[0]
        names = self.model.names
        detected = set()

        for box in results.boxes:
            cls = int(box.cls[0])
            name = names.get(cls, f"class_{cls}")
            detected.add(name)

        if not detected:
            return ["No objects detected."]

        output = []
        for obj in detected:
            if online_mode:
                prompt = f"What is a '{obj}' and what is it used for?"
                desc, _ = get_online_response(prompt)
                output.append(f"{obj.capitalize()}: {desc}")
            else:
                output.append(f"Detected: {obj}")

        return output

# Singleton instance
object_recognizer = ObjectRecognizer()

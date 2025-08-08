import os
import cv2
import time
from ultralytics import YOLO
from ai_modules.online_ai import get_online_response

MODEL_PATH = os.path.join(os.path.dirname(__file__), "yolov8n.pt")  # use yolov8n model for speed

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
        if image_path:
            image = cv2.imread(image_path)
            if image is None:
                return [f"❌ Failed to read image at {image_path}"]
            return self._process_image(image, online_mode)

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return ["❌ Camera not available"]

        print("🔍 Press 'q' to stop scanning.")
        results_texts = []

        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                results = self.model(frame)[0]

                # Draw bounding boxes with colors by confidence
                for box in results.boxes:
                    cls = int(box.cls[0])
                    conf = box.conf[0].item()
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    name = self.model.names.get(cls, f"class_{cls}")

                    # Color logic by confidence
                    if conf > 0.75:
                        color = (0, 255, 0)  # green
                    elif conf > 0.4:
                        color = (0, 255, 255)  # yellow
                    else:
                        color = (0, 0, 255)  # red

                    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                    label = f"{name} {conf*100:.1f}%"
                    cv2.putText(frame, label, (x1, y1 - 10),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

                cv2.imshow("Real-time Object Detection (press 'q' to quit)", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    # On quit, return summary texts
                    detected = set()
                    for box in results.boxes:
                        cls = int(box.cls[0])
                        conf = box.conf[0].item()
                        name = self.model.names.get(cls, f"class_{cls}")
                        detected.add(f"{name} ({conf*100:.1f}%)")

                    if not detected:
                        results_texts.append("No objects detected.")
                    else:
                        results_texts.extend([f"Detected: {obj}" for obj in detected])
                    break

        finally:
            cap.release()
            cv2.destroyAllWindows()

        return results_texts

    def _process_image(self, image, online_mode=False):
        if self.model is None:
            return ["❌ Model not loaded"]

        results = self.model(image)[0]
        detected = set()

        for box in results.boxes:
            cls = int(box.cls[0])
            name = self.model.names.get(cls, f"class_{cls}")
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

object_recognizer = ObjectRecognizer()

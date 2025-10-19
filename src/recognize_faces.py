import os
import cv2
import numpy as np
from deepface import DeepFace
from ultralytics import YOLO 
from PIL import Image


try:
    from src.utils import load_config, load_faiss_data, get_device
except ImportError:
    from utils import load_config, load_faiss_data, get_device


class FaceRecognizer:
    def __init__(self):
        try:
            print("Step 1: Loading configuration...")
            self.config = load_config()
            if not self.config:
                raise Exception("Failed to load project configuration.")
            print("✓ Configuration loaded")
                
            print("Step 2: Getting device...")
            self.device = get_device(self.config)
            print(f"✓ Device set to: {self.device}")

            print("Step 3: Loading FAISS Index and Labels...")
            # 1. Load FAISS Index and Labels


            self.faiss_index, self.labels = load_faiss_data(self.config)
            if self.faiss_index is None:
                raise Exception("FAISS index not loaded. Run precompute_embeddings.py first.")
            print(f"✓ FAISS index loaded with {len(self.labels)} persons: {self.labels}")

            print("Step 4: Loading YOLOv8 Face Detector...")
            # 2. Load YOLOv8 Face Detector (For bounding box on live/new images)
            yolo_model_path = self.config['PATHS']['YOLO_FACE_MODEL']
            print(f"   Loading from: {yolo_model_path}")

            # The YOLOv8 model is loaded onto the correct device for faster inference
            self.yolo_model = YOLO(yolo_model_path).to(self.device)
            print(f"✓ YOLOv8 Face Detector loaded on {self.device}")
            print("Step 5: Configuring DeepFace...")

            # 3. DeepFace Model Configuration (Used for generating the embedding)
            self.embedding_model_name = self.config['RECOGNITION']['EMBEDDING_MODEL']
            self.recognition_threshold = self.config['RECOGNITION']['VERIFICATION_THRESHOLD']
            self.distance_metric = self.config['RECOGNITION']['DISTANCE_METRIC']
            
            
            print(f"✓ DeepFace Embedding Model: {self.embedding_model_name}")
            print("\n✓✓✓ FaceRecognizer initialized successfully! ✓✓✓\n")
            
        except Exception as e:
            import traceback
            print(f"\n❌ Error during initialization at one of the steps:")
            print(f"   {str(e)}")
            print("\nFull traceback:")
            traceback.print_exc()
            raise


    def recognize_face(self, frame: np.ndarray):

        results = []
        
        
        yolo_output = self.yolo_model(frame, verbose=False, device=self.device)
        
        for r in yolo_output:
            
            for box in r.boxes.xyxy: 
                x1, y1, x2, y2 = map(int, box)
                
                
                padding = 10 
                x1 = max(0, x1 - padding)
                y1 = max(0, y1 - padding)
                x2 = min(frame.shape[1], x2 + padding)
                y2 = min(frame.shape[0], y2 + padding)
                
                
                face_crop = frame[y1:y2, x1:x2]
                
                
                person_name = "Unknown"
                min_distance = float('inf')
                
                try:
                    
                    representations = DeepFace.represent(
                        img_path=face_crop,
                        model_name=self.embedding_model_name,
                        enforce_detection=False 
                    )
                    
                    if representations:
                        query_embedding = np.array(representations[0]['embedding']).astype('float32')
                        
    
                        
                        k = 1 
                        
                        distances, indices = self.faiss_index.search(query_embedding[np.newaxis, :], k)
                        
                    
                        min_distance = distances[0][0]
                        best_match_index = indices[0][0]

                        # Check against the verification threshold
                        if min_distance <= self.recognition_threshold:
                            person_name = self.labels[best_match_index]
                            
                        
                        
                except Exception as e:
                    pass # Keep label as "Unknown"

            
                results.append({
                    'box': (x1, y1, x2 - x1, y2 - y1), # (x, y, w, h) format
                    'label': person_name,
                    'distance': min_distance
                })
                
        return results


def draw_results(frame, recognition_results):
    for result in recognition_results:
        x, y, w, h = result['box']
        label = result['label']
        distance = result['distance']

        color = (0, 255, 0) if label != "Unknown" else (0, 0, 255) # Green for known, Red for unknown
        
        # Draw bounding box
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
        
        # Draw label text
        text = f"{label} ({distance:.2f})"
        cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        
    return frame


if __name__ == "__main__":
    
    try:
        recognizer = FaceRecognizer()
        print("FaceRecognizer initialized successfully!")
        print(f"Loaded {len(recognizer.labels)} persons: {recognizer.labels}")
    except Exception as e:
        print(f"Failed to initialize FaceRecognizer: {e}")
        print("Please ensure:")
        print("  1. Dataset is populated in 'dataset/' folder")
        print("  2. Run 'python src/precompute_embeddings.py' first")
        exit()
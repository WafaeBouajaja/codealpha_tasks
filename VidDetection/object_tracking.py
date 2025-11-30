"""
object_tracking.py - Modules de détection et tracking corrigés                                       
"""

import cv2
import numpy as np
from ultralytics import YOLO
from deep_sort_realtime.deepsort_tracker import DeepSort


class ObjectDetector:
    """Détection d'objets avec YOLO"""
    
    def __init__(self, model_name='yolov8n.pt', confidence_threshold=0.5):
        print(f"📦 Chargement du modèle YOLO: {model_name}...")
        self.model = YOLO(model_name)
        self.confidence_threshold = confidence_threshold
        np.random.seed(42)
        self.colors = np.random.randint(0, 255, size=(100, 3), dtype=np.uint8)
        print("✅ Modèle YOLO chargé!")
        
    def detect(self, frame):
        """Détecte les objets dans une frame"""
        results = self.model(frame, verbose=False)[0]
        detections = []
        
        for box in results.boxes:
            conf = float(box.conf[0])
            if conf >= self.confidence_threshold:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                class_id = int(box.cls[0])
                class_name = results.names[class_id]
                
                detections.append({
                    "bbox": [x1, y1, x2, y2],
                    "confidence": float(conf),  # Convertir en float natif
                    "class_id": int(class_id),  # Convertir en int natif
                    "class_name": class_name
                })
        
        return detections
    
    def draw_detections(self, frame, detections):
        """Dessine les détections sur la frame"""
        annotated_frame = frame.copy()
        
        for det in detections:
            x1, y1, x2, y2 = det['bbox']
            conf = det['confidence']
            class_name = det['class_name']
            class_id = det['class_id']
            
            # Couleur basée sur la classe
            color = self.colors[class_id % 100].tolist()
            
            # Dessiner la boîte
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 2)
            
            # Label
            label = f"{class_name}: {conf:.2f}"
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 2
            )
            
            # Fond pour le texte
            cv2.rectangle(
                annotated_frame,
                (x1, y1 - text_height - 10),
                (x1 + text_width, y1),
                color,
                -1
            )
            
            # Texte
            cv2.putText(
                annotated_frame, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2
            )
        
        return annotated_frame


class ObjectTracker:
    """Tracking avec Deep SORT"""
    
    def __init__(self):
        print("🎯 Initialisation du tracker Deep SORT...")
        self.tracker = DeepSort(
            max_age=30,
            n_init=3,
            nms_max_overlap=1.0,
            max_cosine_distance=0.3,
            nn_budget=None,
            override_track_class=None,
            embedder="mobilenet",
            half=True,
            bgr=True,
            embedder_gpu=True,
        )
        np.random.seed(42)
        self.colors = np.random.randint(0, 255, size=(100, 3), dtype=np.uint8)
        print("✅ Tracker Deep SORT initialisé!")
    
    def update(self, frame, detections):
        """Met à jour le tracker avec les nouvelles détections"""
        if len(detections) == 0:
            self.tracker.tracker.predict()
            self.tracker.tracker.update([])
            return []
        
        detection_list = []
        for det in detections:
            x1, y1, x2, y2 = det["bbox"]
            w = x2 - x1
            h = y2 - y1
            conf = det["confidence"]
            class_name = det["class_name"]
            detection_list.append(([x1, y1, w, h], conf, class_name))
        
        tracks = self.tracker.update_tracks(detection_list, frame=frame)
        return tracks
    
    def get_track_info(self, tracks):
        """Extrait les informations des tracks pour JSON"""
        track_info = []
        
        for track in tracks:
            if track.is_confirmed():
                # Conversion sécurisée de l'ID
                try:
                    tid = int(track.track_id)
                except (ValueError, TypeError):
                    tid = str(track.track_id)
                
                track_info.append({
                    "id": tid,
                    "class": track.get_det_class() if track.get_det_class() else "Unknown",
                    "bbox": [int(x) for x in track.to_ltrb()]  # Convertir en int natif
                })
        
        return track_info
    
    def draw_tracks(self, frame, tracks):
        """Dessine les tracks sur la frame"""
        annotated_frame = frame.copy()
        
        for track in tracks:
            if not track.is_confirmed():
                continue
            
            track_id = track.track_id
            ltrb = track.to_ltrb()
            x1, y1, x2, y2 = map(int, ltrb)
            
            # Conversion sécurisée de l'ID pour les couleurs
            try:
                tid = int(track_id)
            except (ValueError, TypeError):
                tid = hash(str(track_id)) % 100
            
            color = self.colors[tid % 100].tolist()
            
            # Dessiner la boîte
            cv2.rectangle(annotated_frame, (x1, y1), (x2, y2), color, 3)
            
            # Label avec ID et classe
            class_name = track.get_det_class() if track.get_det_class() else "Unknown"
            label = f"ID:{track_id} {class_name}"
            
            (text_width, text_height), _ = cv2.getTextSize(
                label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
            )
            
            # Fond pour le texte
            cv2.rectangle(
                annotated_frame,
                (x1, y1 - text_height - 10),
                (x1 + text_width, y1),
                color,
                -1
            )
            
            # Texte
            cv2.putText(
                annotated_frame, label, (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2
            )
        
        return annotated_frame
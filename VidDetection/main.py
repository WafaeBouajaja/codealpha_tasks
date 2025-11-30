"""                                                       
main.py - FastAPI Backend pour détection et tracking vidéo
"""

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from object_tracking import ObjectDetector, ObjectTracker
import cv2
import numpy as np
import tempfile
import os
import io
from typing import List, Dict

app = FastAPI(title="Object Detection & Tracking API")

# CORS pour permettre Streamlit de communiquer
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser les modèles au démarrage
print("🚀 Initialisation des modèles...")
detector = ObjectDetector(model_name='yolov8n.pt', confidence_threshold=0.5)
tracker = ObjectTracker()
print("✅ Serveur prêt!")


@app.get("/")
async def root():
    """Page d'accueil de l'API"""
    return {
        "message": "API de Détection et Tracking d'Objets",
        "endpoints": {
            "/detect-video": "POST - Analyser une vidéo",
            "/detect-video-stream": "POST - Traiter et retourner la vidéo annotée",
            "/health": "GET - Vérifier l'état du serveur"
        }
    }


@app.get("/health")
async def health_check():
    """Vérifier l'état du serveur"""
    return {"status": "ok", "models_loaded": True}


@app.post("/detect-video")
async def detect_video(file: UploadFile = File(...)):
    """
    Analyse une vidéo et retourne les détections/tracks pour chaque frame
    """
    if not file.filename.endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(status_code=400, detail="Format vidéo non supporté. Utilisez MP4, AVI ou MOV.")
    
    # Sauvegarder temporairement la vidéo
    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        cap = cv2.VideoCapture(tmp_path)
        
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Impossible d'ouvrir la vidéo")
        
        frames_data = []
        frame_count = 0
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        print(f"📹 Traitement de {total_frames} frames...")
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Détection
            detections = detector.detect(frame)
            
            # Tracking
            tracks = tracker.update(frame, detections)
            track_info = tracker.get_track_info(tracks)
            
            # Sauvegarder les résultats (limité pour éviter une réponse trop lourde)
            if frame_count % 10 == 0 or frame_count < 5:  # Échantillonnage
                frames_data.append({
                    "frame_number": frame_count,
                    "detections": detections,
                    "tracks": track_info
                })
            
            frame_count += 1
            
            # Progression
            if frame_count % 50 == 0:
                print(f"  Progression: {frame_count}/{total_frames} frames")
        
        cap.release()
        
        print(f"✅ Traitement terminé: {frame_count} frames")
        
        return {
            "status": "success",
            "total_frames": frame_count,
            "sampled_frames": len(frames_data),
            "frames": frames_data
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors du traitement: {str(e)}")
    
    finally:
        # Nettoyer le fichier temporaire
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


@app.post("/detect-video-stream")
async def detect_video_stream(file: UploadFile = File(...)):
    """
    Traite une vidéo et retourne la vidéo annotée
    """
    if not file.filename.endswith(('.mp4', '.avi', '.mov')):
        raise HTTPException(status_code=400, detail="Format vidéo non supporté")
    
    # Sauvegarder temporairement
    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_in:
        content = await file.read()
        tmp_in.write(content)
        tmp_in_path = tmp_in.name
    
    # Fichier de sortie temporaire
    tmp_out_path = tempfile.mktemp(suffix='.mp4')
    
    try:
        cap = cv2.VideoCapture(tmp_in_path)
        
        if not cap.isOpened():
            raise HTTPException(status_code=400, detail="Impossible d'ouvrir la vidéo")
        
        # Propriétés vidéo
        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        # Writer pour la vidéo de sortie
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(tmp_out_path, fourcc, fps, (frame_width, frame_height))
        
        print(f"📹 Traitement et annotation de la vidéo...")
        
        frame_count = 0
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            
            # Détection
            detections = detector.detect(frame)
            
            # Tracking
            tracks = tracker.update(frame, detections)
            
            # Dessiner les annotations
            annotated_frame = tracker.draw_tracks(frame, tracks)
            
            # Écrire la frame annotée
            out.write(annotated_frame)
            
            frame_count += 1
            if frame_count % 50 == 0:
                print(f"  Frames traitées: {frame_count}")
        
        cap.release()
        out.release()
        
        print(f"✅ Vidéo annotée créée: {frame_count} frames")
        
        # Lire la vidéo annotée
        with open(tmp_out_path, 'rb') as f:
            video_bytes = f.read()
        
        # Retourner la vidéo
        return StreamingResponse(
            io.BytesIO(video_bytes),
            media_type="video/mp4",
            headers={"Content-Disposition": f"attachment; filename=annotated_{file.filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur: {str(e)}")
    
    finally:
        # Nettoyer les fichiers temporaires
        for path in [tmp_in_path, tmp_out_path]:
            if os.path.exists(path):
                os.remove(path)


if __name__ == "__main__":
    import uvicorn
    print("\n" + "="*60)
    print("🚀 Démarrage du serveur FastAPI")
    print("="*60)
    print("📍 URL: http://127.0.0.1:8000")
    print("📚 Documentation: http://127.0.0.1:8000/docs")
    print("="*60 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
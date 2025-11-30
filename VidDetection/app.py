"""
app.py - Interface Streamlit pour la détection et tracking d'objets    
"""

import streamlit as st
import requests
import io
import time

# Configuration de la page
st.set_page_config(
    page_title="Détection & Tracking d'Objets",
    page_icon="🎯",
    layout="wide"
)

# URL de l'API
API_URL = "http://127.0.0.1:8000"

# Style personnalisé
st.markdown("""
    <style>
    .big-font {
        font-size:20px !important;
        font-weight: bold;
    }
    .success-box {
        padding: 10px;
        border-radius: 5px;
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
    }
    </style>
    """, unsafe_allow_html=True)


def check_api_health():
    """Vérifie si l'API est accessible"""
    try:
        response = requests.get(f"{API_URL}/health", timeout=2)
        return response.status_code == 200
    except:
        return False


def main():
    # Titre
    st.title("🎯 Système de Détection et Tracking d'Objets")
    st.markdown("---")
    
    # Vérifier l'état de l'API
    col1, col2 = st.columns([3, 1])
    
    with col2:
        if check_api_health():
            st.success("✅ API connectée")
        else:
            st.error("❌ API non disponible")
            st.info("Lancez le serveur : `python main.py`")
            return
    
    # Onglets
    tab1, tab2, tab3 = st.tabs(["📹 Analyse Vidéo", "🎥 Vidéo Annotée", "ℹ️ Informations"])
    
    # ========== ONGLET 1: Analyse de données ==========
    with tab1:
        st.header("📹 Analyse de Vidéo (Données)")
        st.markdown("Téléchargez une vidéo pour obtenir les détections et tracks")
        
        uploaded_file = st.file_uploader(
            "Choisir une vidéo",
            type=["mp4", "avi", "mov"],
            key="video_analyzer"
        )
        
        if uploaded_file:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.video(uploaded_file)
            
            with col2:
                st.info(f"""
                **Fichier:** {uploaded_file.name}
                
                **Taille:** {uploaded_file.size / (1024*1024):.2f} MB
                
                Cette analyse retournera les détections et tracks pour chaque frame échantillonnée.
                """)
            
            if st.button("🔍 Analyser la vidéo", type="primary", key="analyze_btn"):
                with st.spinner("⏳ Analyse en cours... Cela peut prendre quelques minutes..."):
                    try:
                        # Envoyer la vidéo à l'API
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                        response = requests.post(
                            f"{API_URL}/detect-video",
                            files=files,
                            timeout=300  # 5 minutes timeout
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            # Afficher les résultats
                            st.success("✅ Analyse terminée avec succès!")
                            
                            # Statistiques globales
                            st.markdown("### 📊 Statistiques")
                            col1, col2, col3 = st.columns(3)
                            
                            with col1:
                                st.metric("Total Frames", data['total_frames'])
                            
                            with col2:
                                st.metric("Frames Analysées", data['sampled_frames'])
                            
                            with col3:
                                # Compter les objets uniques
                                all_classes = set()
                                for frame_data in data['frames']:
                                    for det in frame_data['detections']:
                                        all_classes.add(det['class_name'])
                                st.metric("Classes Détectées", len(all_classes))
                            
                            # Afficher les classes détectées
                            if all_classes:
                                st.markdown("### 🏷️ Classes d'Objets Détectées")
                                st.write(", ".join(sorted(all_classes)))
                            
                            # Afficher quelques frames échantillonnées
                            st.markdown("### 📋 Détails des Frames (échantillon)")
                            
                            for i, frame_data in enumerate(data["frames"][:10]):  # Limiter à 10 frames
                                with st.expander(f"Frame {frame_data['frame_number']}"):
                                    col1, col2 = st.columns(2)
                                    
                                    with col1:
                                        st.markdown("**Détections:**")
                                        if frame_data["detections"]:
                                            for j, det in enumerate(frame_data["detections"], 1):
                                                st.write(f"{j}. **{det['class_name']}** - Confiance: {det['confidence']:.2%}")
                                        else:
                                            st.write("Aucune détection")
                                    
                                    with col2:
                                        st.markdown("**Tracks:**")
                                        if frame_data["tracks"]:
                                            for track in frame_data["tracks"]:
                                                st.write(f"ID {track['id']}: {track['class']}")
                                        else:
                                            st.write("Aucun track")
                            
                            # Option de téléchargement JSON
                            import json
                            json_str = json.dumps(data, indent=2)
                            st.download_button(
                                label="📥 Télécharger les données JSON",
                                data=json_str,
                                file_name=f"analysis_{uploaded_file.name}.json",
                                mime="application/json"
                            )
                        
                        else:
                            st.error(f"❌ Erreur {response.status_code}: {response.text}")
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Timeout: La vidéo est trop longue. Essayez une vidéo plus courte.")
                    
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
    
    # ========== ONGLET 2: Vidéo annotée ==========
    with tab2:
        st.header("🎥 Génération de Vidéo Annotée")
        st.markdown("Téléchargez une vidéo pour obtenir une version avec les détections et tracks dessinés")
        
        uploaded_file2 = st.file_uploader(
            "Choisir une vidéo",
            type=["mp4", "avi", "mov"],
            key="video_annotator"
        )
        
        if uploaded_file2:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.video(uploaded_file2)
            
            with col2:
                st.info(f"""
                **Fichier:** {uploaded_file2.name}
                
                **Taille:** {uploaded_file2.size / (1024*1024):.2f} MB
                
                Cette option génère une vidéo avec les boîtes de détection et IDs de tracking dessinés.
                """)
            
            if st.button("🎨 Générer vidéo annotée", type="primary", key="annotate_btn"):
                with st.spinner("⏳ Traitement et annotation... Cela peut prendre plusieurs minutes..."):
                    try:
                        # Envoyer la vidéo à l'API
                        files = {"file": (uploaded_file2.name, uploaded_file2.getvalue(), uploaded_file2.type)}
                        response = requests.post(
                            f"{API_URL}/detect-video-stream",
                            files=files,
                            timeout=600  # 10 minutes timeout
                        )
                        
                        if response.status_code == 200:
                            st.success("✅ Vidéo annotée générée avec succès!")
                            
                            # Afficher la vidéo annotée
                            st.markdown("### 🎬 Vidéo Annotée")
                            video_bytes = response.content
                            st.video(video_bytes)
                            
                            # Bouton de téléchargement
                            st.download_button(
                                label="📥 Télécharger la vidéo annotée",
                                data=video_bytes,
                                file_name=f"annotated_{uploaded_file2.name}",
                                mime="video/mp4"
                            )
                        
                        else:
                            st.error(f"❌ Erreur {response.status_code}: {response.text}")
                    
                    except requests.exceptions.Timeout:
                        st.error("⏱️ Timeout: La vidéo est trop longue. Essayez une vidéo plus courte.")
                    
                    except Exception as e:
                        st.error(f"❌ Erreur: {str(e)}")
    
    # ========== ONGLET 3: Informations ==========
    with tab3:
        st.header("ℹ️ Informations sur le Système")
        
        st.markdown("""
        ### 🎯 Système de Détection et Tracking d'Objets
        
        Ce système utilise:
        - **YOLOv8** pour la détection d'objets en temps réel
        - **Deep SORT** pour le tracking multi-objets
        - **FastAPI** pour le backend
        - **Streamlit** pour l'interface web
        
        ### 📋 Fonctionnalités
        
        **Onglet 1 - Analyse Vidéo:**
        - Analyse frame par frame
        - Extraction des détections et tracks
        - Export des données en JSON
        - Statistiques détaillées
        
        **Onglet 2 - Vidéo Annotée:**
        - Génération d'une vidéo avec annotations visuelles
        - Boîtes de détection colorées
        - IDs de tracking persistants
        - Téléchargement de la vidéo annotée
        
        ### 🏷️ Classes Détectables
        
        Le système peut détecter plus de 80 classes d'objets du dataset COCO, incluant:
        - 👤 Personnes
        - 🚗 Véhicules (voiture, moto, bus, camion, vélo)
        - 🐕 Animaux (chien, chat, cheval, vache, mouton, oiseau)
        - ⚽ Sports (ballon, frisbee, skis, snowboard)
        - 🪑 Meubles (chaise, canapé, table, lit)
        - 📱 Électronique (téléphone, ordinateur, TV, clavier, souris)
        - Et bien plus...
        
        ### ⚙️ Configuration
        
        **Modèle actuel:** YOLOv8 Nano (rapide)
        
        **Seuil de confiance:** 0.5 (50%)
        
        ### 🚀 Pour démarrer
        
        1. Assurez-vous que l'API est lancée:
        ```bash
        python main.py
        ```
        
        2. Lancez l'interface Streamlit:
        ```bash
        streamlit run app.py
        ```
        
        ### 📊 Performance
        
        - **YOLOv8n**: ~45 FPS (GPU) / ~15 FPS (CPU)
        - **Temps de traitement**: ~2-5 minutes pour une vidéo de 30s
        
        ### 🆘 Support
        
        En cas de problème:
        - Vérifiez que l'API est en cours d'exécution
        - Vérifiez la taille de la vidéo (< 100MB recommandé)
        - Consultez les logs du serveur FastAPI
        """)
        
        # Informations système
        st.markdown("### 💻 État du Système")
        
        if check_api_health():
            st.success("✅ API opérationnelle")
            st.info(f"🔗 URL API: {API_URL}")
            st.info(f"📚 Documentation: {API_URL}/docs")
        else:
            st.error("❌ API non accessible")
            st.code("python main.py", language="bash")


if __name__ == "__main__":
    main()
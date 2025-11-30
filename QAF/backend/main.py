# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
import string
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import word_tokenize
from sentence_transformers import SentenceTransformer, util
import torch

# ==============================
# NLP Setup
# ==============================
# Assurer que toutes les ressources nécessaires sont présentes
for resource in ["punkt", "punkt_tab", "stopwords", "wordnet"]:
    try:
        nltk.data.find(f"tokenizers/{resource}" if "punkt" in resource else f"corpora/{resource}")
    except LookupError:
        nltk.download(resource, quiet=True)

stop_words = set(stopwords.words("english"))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    text = text.lower()
    tokens = word_tokenize(text)
    tokens = [t for t in tokens if t not in stop_words and t not in string.punctuation]
    tokens = [lemmatizer.lemmatize(t) for t in tokens]
    return " ".join(tokens)

# ==============================
# Load FAQ dataset
# ==============================
with open("qaf.json", "r", encoding="utf-8") as f:
    faq_data = json.load(f)

questions = [q["question"] for q in faq_data]
answers = [q["answer"] for q in faq_data]

# ==============================
# Sentence-BERT model
# ==============================
model = SentenceTransformer('all-MiniLM-L6-v2')
print("Model loaded successfully")
question_embeddings = model.encode(questions, convert_to_tensor=True)

# ==============================
# FastAPI setup
# ==============================
class ChatRequest(BaseModel):
    message: str

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True
)

# ==============================
# Bot response function
# ==============================
def get_bot_response(user_message):
    processed_message = preprocess(user_message)
    user_embedding = model.encode(processed_message, convert_to_tensor=True)

    cos_scores = util.pytorch_cos_sim(user_embedding, question_embeddings)
    top_score, top_idx = torch.max(cos_scores, dim=1)

    if top_score < 0.5:
        return "Sorry, I don't understand. Can you rephrase?"

    return answers[top_idx.item()]

# ==============================
# API endpoint
# ==============================
@app.post("/chat")
async def chat(request: ChatRequest):
    reply = get_bot_response(request.message)
    return {"reply": reply}

# ==============================
# Run via: uvicorn main:app --reload
# ==============================

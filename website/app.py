import warnings
from flask import Flask, request, jsonify
from flask_cors import CORS
import main  
from main import tutto
from openai import OpenAI
import os
import faiss
from dotenv import load_dotenv
from pydantic import BaseModel
from packages.vector import get_vector_store, get_chunks, find_articles, split_articles, question_article_dic
from langchain_community.vectorstores import FAISS
from langchain_community.embeddings import OpenAIEmbeddings
from typing import List, Dict
import json



app = Flask(__name__)

# parte importata da main

with open('C:/Users/aless/lai/venv/testiLeggi/gdpr.txt', 'r', encoding='utf-8') as file:
    gdpr = file.read() 
with open('C:/Users/aless/lai/venv/testiLeggi/AIACT.txt', 'r', encoding='utf-8') as file:
    aiact = file.read() 



warnings.filterwarnings('ignore')
load_dotenv()  
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

gdpr_faiss_store = FAISS.load_local("C:/Users/aless/lai/venv/gdpr_vec_store",
                                     embeddings,
                                     allow_dangerous_deserialization=True)
aiact_faiss_store = FAISS.load_local("C:/Users/aless/lai/venv/aiact_vec_store", 
                                     embeddings,
                                     allow_dangerous_deserialization=True)




CORS(app)  # Permette le richieste CORS dal frontend

# Funzione di esempio per elaborare i dati
# Funzione per chiamare tutto con le sei risposte
def call_tutto(data):
    # Prendi le sei risposte inviate dal frontend
    answer0 = data.get("answer0", "")
    answer1 = data.get("answer1", "")
    answer2 = data.get("answer2", "")
    answer3 = data.get("answer3", "")
    answer4 = data.get("answer4", "")
    answer5 = data.get("answer5", "")
    
    # Chiama la funzione `tutto` con le sei risposte
    risposte_gdpr, risposte_aiact = tutto(answer0, answer1, answer2, answer3, answer4, answer5)
    
    # Prepara la risposta in formato JSON
    result = {
        "GDPR": [
            {"domanda": r[0], "risposta": r[1], "voto": r[2]} for r in risposte_gdpr
        ],
        "AIACT": [
            {"domanda": r[0], "risposta": r[1], "voto": r[2]} for r in risposte_aiact
        ]
    }
    return result


@app.route('/process', methods=['POST'])
def process():
    data = request.json  # Ricevi i dati in formato JSON
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Chiama la funzione che usa `tutto` con i dati ricevuti
    result = call_tutto(data)
    
    # Restituisci la risposta come JSON
    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)


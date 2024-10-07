import warnings
from flask import Flask, request, jsonify
from flask_cors import CORS
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
CORS(app)
  # Permette le richieste CORS dal frontend
# parte importata da main

with open('C:/Users/aless/lai/venv/testiLeggi/gdpr.txt', 'r', encoding='utf-8') as file:
    gdpr = file.read() 
with open('C:/Users/aless/lai/venv/testiLeggi/AIACT.txt', 'r', encoding='utf-8') as file:
    aiact = file.read() 



warnings.filterwarnings('ignore')
load_dotenv()  
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)

gdpr_faiss_store = FAISS.load_local("C:/Users/aless/OneDrive/Documenti/GitHub/LAI/gdpr_vec_store",
                                        embeddings,
                                        allow_dangerous_deserialization=True)
aiact_faiss_store = FAISS.load_local("C:/Users/aless/OneDrive/Documenti/GitHub/LAI/aiact_vec_store", 
                                        embeddings,
                                        allow_dangerous_deserialization=True)





from flask import jsonify

def call_tutto(data):
    # Logga i dati ricevuti
    app.logger.debug(f"Data received: {data}")
    
    # Prendi le sei risposte inviate dal frontend
    answers = [data.get(f"answer{i}", None) for i in range(6)]
    
    # Controlla che tutte le risposte siano presenti
    if any(answer is None for answer in answers):
        app.logger.warning("Some answers are missing.")
        return jsonify({"error": "One or more answers are missing"}), 400
    else:
        app.logger.debug("All answers received correctly.")
        
    # Chiama la funzione `tutto` con le sei risposte
    risposte_gdpr, risposte_aiact = tutto(*answers)
    
    # Prepara la risposta in formato JSON
    result = {
        "GDPR": [
            {"domanda": r[0], "risposta": r[1], "voto": r[2]} for r in risposte_gdpr
        ],
        "AIACT": [
            {"domanda": r[0], "risposta": r[1], "voto": r[2]} for r in risposte_aiact
        ]
    }
    return jsonify(result)

print(66)
@app.route('/process', methods=['POST'])
def process():
    data = request.json
    print(67)
    app.logger.debug(f"Data received: {data}")  # Log received data
    if not data:
        return jsonify({"error": "No data provided"}), 400

    result = call_tutto(data)
    app.logger.debug(f"Result generated: {result}")  # Log the result

    return jsonify(result), 200


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)


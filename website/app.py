from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Permette le richieste CORS dal frontend

# Funzione di esempio per elaborare i dati
def process_data(data):
    # Qui puoi integrare il tuo codice Python per elaborare i dati
    # Ad esempio, potresti salvare i dati, analizzarli, ecc.
    # Questo è solo un esempio di risposta
    nome_startup = data.get("nome_startup", "N/A")
    settore = data.get("settore", "N/A")
    paese = data.get("paese", "N/A")
    modello_business = data.get("modello_business", "N/A")
    team = data.get("team", "N/A")
    sfide = data.get("sfide", "N/A")
    
    # Genera una risposta basata sui dati
    risposta = f"Grazie per le informazioni! La tua startup '{nome_startup}' nel settore '{settore}' ha intenzione di espandersi in '{paese}' con un modello di business '{modello_business}'. Il tuo team conta {team} membri e le principali sfide sono: {sfide}."
    return risposta

@app.route('/process', methods=['POST'])
def process():
    data = request.json  # Ricevi i dati in formato JSON
    if not data:
        return jsonify({"error": "No data provided"}), 400
    
    # Elabora i dati
    risposta = process_data(data)
    
    # Restituisci la risposta
    return jsonify({"bot_response": risposta}), 200

if __name__ == '__main__':
    app.run(debug=True)


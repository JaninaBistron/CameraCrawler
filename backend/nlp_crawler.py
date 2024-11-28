from flask import Flask, jsonify, request
from flask_cors import CORS  # Importiere CORS, um Cross-Origin-Anfragen zu erlauben: Backend und Frontend liegen auf unterschiedlichen Domains laufen

app = Flask(__name__)

# Aktiviere CORS für alle Routen
CORS(app)

# API-Endpunkt ("Schnittstelle") für POST-Anfragen, um user_input zu empfangen und zu verarbeiten
@app.route('/api/calculate', methods=['POST'])
def calculate():
    # Empfang des JSON-Body mit der "user_input"-Variable
    data = request.get_json()

    # Diesen Teil ersetzen wir später durch den echten Pythoncode!
    # Überprüfen, ob "user_input" im empfangenen JSON enthalten ist
    if 'user_input' not in data:
        return jsonify({"error": "Missing 'user_input' in request data"}), 400
    try:
        # user_input wird als Zahl erwartet, daher wird versucht, ihn in einen Integer zu konvertieren
        user_input = int(data['user_input'])
        # Berechnung
        script_output = user_input + 10
        # Rückgabe des Ergebnisses als JSON
        return jsonify({"script_output": script_output})
    except ValueError:
        # Falls user_input keine Zahl ist, eine Fehlermeldung zurückgeben
        return jsonify({"error": "'user_input' must be a number"}), 400

if __name__ == '__main__':
    # In der Produktionsumgebung von Heroku wird das Port automatisch gesetzt, daher müssen wir den Host anpassen
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

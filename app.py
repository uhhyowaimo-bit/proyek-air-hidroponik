# app.py
from flask import Flask, render_template, jsonify, request
import os
from datetime import datetime

app = Flask(__name__)

# Simpan data terakhir dari ESP32 (di memori)
latest_sensor_data = None

# Simpan hasil prediksi dari aplikasi offline (di memori)
latest_prediction = None

# Ganti dengan secret key unikmu (simpan di Render sebagai environment variable)
SECRET_KEY = os.environ.get("PREDICTION_SECRET_KEY", "hidroponik-rahasia-123")

def evaluate_status(tds, ec, temp):
    tds_good = 400 <= tds <= 1200
    ec_good = 0.8 <= ec <= 2.4
    temp_good = 18 <= temp <= 24

    if tds_good and ec_good and temp_good:
        return "BAIK", "success", "Air ideal untuk tanaman."
    elif (200 <= tds <= 1500) and (0.4 <= ec <= 3.0) and (15 <= temp <= 28):
        return "SEDANG", "warning", "Periksa nutrisi, pertimbangkan penggantian air."
    else:
        return "BURUK", "danger", "Segera lakukan tindakan! Risiko tinggi bagi tanaman."

@app.route('/api/data', methods=['POST'])
def receive_sensor_data():
    """Terima data real-time dari ESP32"""
    global latest_sensor_data
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON"}), 400

        tds = float(data.get('tds', 0))
        ec = float(data.get('ec', 0))
        temp = float(data.get('temp', 0))

        latest_sensor_data = {
            "timestamp": datetime.now().isoformat(),
            "tds": tds,
            "ec": ec,
            "temp": temp
        }
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/latest')
def get_latest():
    if latest_sensor_data is None:
        return jsonify({"error": "No data"})

    status, color, rec = evaluate_status(
        latest_sensor_data["tds"],
        latest_sensor_data["ec"],
        latest_sensor_data["temp"]
    )

    return jsonify({
        "timestamp": latest_sensor_data["timestamp"],
        "tds": latest_sensor_data["tds"],
        "ec": latest_sensor_data["ec"],
        "temp": latest_sensor_data["temp"],
        "status": status,
        "bootstrap_color": color,
        "recommendation": rec
    })

@app.route('/api/upload-prediction', methods=['POST'])
def upload_prediction():
    """Hanya aplikasi offline yang tahu SECRET_KEY yang boleh kirim"""
    global latest_prediction
    try:
        data = request.get_json()
        if not data or data.get('key') != SECRET_KEY:
            return jsonify({"error": "Unauthorized"}), 401

        latest_prediction = {
            "timestamp": datetime.now().isoformat(),
            "forecast": data.get("forecast", [])
        }
        return jsonify({"status": "success"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/api/prediction')
def get_prediction():
    if latest_prediction is None:
        return jsonify({"error": "No prediction"})
    return jsonify(latest_prediction)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
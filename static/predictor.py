# predictor.py
import pandas as pd
import requests
import sys
import os
from statsmodels.tsa.arima.model import ARIMA

# === KONFIGURASI ===
WEB_URL = "https://namaweb.onrender.com"  # GANTI DENGAN URL WEB-MU
SECRET_KEY = "hidroponik-rahasia-123"     # HARUS SAMA DENGAN DI app.py

def main():
    print("=== Aplikasi Prediksi Hidroponik (Offline) ===")
    
    # 1. Minta path file CSV
    csv_path = input("Masukkan path file sensor.csv dari microSD: ").strip()
    if not os.path.exists(csv_path):
        print("❌ File tidak ditemukan!")
        return

    # 2. Baca data
    try:
        df = pd.read_csv(csv_path, names=["timestamp", "tds", "ec", "temp"])
        print(f"✅ Terbaca {len(df)} data dari microSD.")
    except Exception as e:
        print("❌ Gagal baca file:", e)
        return

    # 3. Prediksi TDS 6 jam ke depan (ARIMA sederhana)
    try:
        model = ARIMA(df['tds'].dropna(), order=(1,1,1))
        fitted = model.fit()
        forecast = fitted.forecast(steps=6).tolist()
        print("✅ Prediksi selesai:", [round(x) for x in forecast])
    except Exception as e:
        print("⚠️ Gagal prediksi, gunakan data dummy:", e)
        forecast = [df['tds'].iloc[-1]] * 6  # fallback

    # 4. Kirim ke web
    try:
        response = requests.post(f"{WEB_URL}/api/upload-prediction", json={
            "key": SECRET_KEY,
            "forecast": forecast
        }, timeout=10)
        
        if response.status_code == 200:
            print("📤 Hasil prediksi berhasil dikirim ke web!")
            print("🌐 Buka web Anda untuk melihat hasilnya.")
        else:
            print("❌ Gagal kirim ke web:", response.text)
    except Exception as e:
        print("❌ Error kirim ke web:", e)

if __name__ == "__main__":
    main()
import os

import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

sleep_model = joblib.load(os.path.join(MODEL_DIR, "sleep_model.keras"))
sleep_scaler = joblib.load(os.path.join(MODEL_DIR, "sleep_scaler.pkl"))
productivity_model = joblib.load(os.path.join(MODEL_DIR, "productivity_model.keras"))
productivity_scaler = joblib.load(os.path.join(MODEL_DIR, "productivity_scaler.pkl"))

# Mapping frekuensi form -> nilai numerik (lihat PRD §4.C)
PHONE_USAGE_MAP = {"Tidak": 0.0, "Jarang": 1.0, "Sering": 2.0, "Selalu": 3.0}
COFFEE_INTAKE_MAP = {"Tidak": 0, "Jarang": 100, "Sering": 250, "Selalu": 400}
KESULITAN_ADJUSTMENT_MAP = {"Tidak": 0.0, "Jarang": 0.0, "Sering": 10.0, "Selalu": 20.0}

PRODUCTIVITY_LABELS = ["Rendah", "Sedang", "Tinggi"]

# Rentang fitur saat training Model 1 — clip agar input ekstrem tetap stabil
SLEEP_FEATURE_BOUNDS = [
    (5.8, 8.5),   # Sleep Duration
    (4, 9),       # Quality of Sleep
    (30, 90),     # Physical Activity Level
    (3, 8),       # Stress Level
]


def _clip(values, bounds):
    return [min(max(v, lo), hi) for v, (lo, hi) in zip(values, bounds)]


def _insomnia_category(score):
    if score < 25:
        return "Tidak Ada Gejala"
    if score < 50:
        return "Subthreshold"
    if score < 75:
        return "Sedang"
    return "Berat"


def _build_analysis(durasi_tidur, kualitas_tidur, aktivitas_fisik, layar, kafein,
                    kesulitan, insomnia_label, prod_label):
    triggers = []
    if durasi_tidur < 7:
        triggers.append(f"durasi tidur pendek ({durasi_tidur} jam)")
    if kualitas_tidur < 6:
        triggers.append(f"kualitas tidur rendah ({kualitas_tidur}/10)")
    if aktivitas_fisik < 60:
        triggers.append(f"aktivitas fisik minim ({aktivitas_fisik} menit)")
    if layar in ("Sering", "Selalu"):
        triggers.append(f"paparan layar {layar.lower()} sebelum tidur")
    if kafein in ("Sering", "Selalu"):
        triggers.append(f"konsumsi kafein {kafein.lower()}")
    if kesulitan in ("Sering", "Selalu"):
        triggers.append(f"kesulitan tidur {kesulitan.lower()}")

    head = f"Produktivitas terprediksi {prod_label}, indikasi insomnia: {insomnia_label}."
    if triggers:
        return head + " Pemicu utama: " + "; ".join(triggers) + "."
    return head + " Pola tidur tergolong sehat, pertahankan kebiasaan baik."


def preprocess_inputs(durasi_tidur, kualitas_tidur, aktivitas_fisik, tingkat_stres,
                      layar_sebelum_tidur, konsumsi_kafein, kesulitan_tidur):
    """Jalankan 2 model JST + hybrid scoring. Return dict untuk result.html."""
    durasi_tidur = float(durasi_tidur)
    kualitas_tidur = int(kualitas_tidur)
    aktivitas_fisik = int(aktivitas_fisik)
    tingkat_stres = int(tingkat_stres)

    # --- Model 1: Insomnia (Sleep Duration, Quality, Physical Activity, Stress) ---
    x1 = _clip([durasi_tidur, kualitas_tidur, aktivitas_fisik, tingkat_stres], SLEEP_FEATURE_BOUNDS)
    prob_insomnia = sleep_model.predict_proba(sleep_scaler.transform([x1]))[0][1] * 100

    # Hybrid Scoring (PRD §4.C): tambah adjustment dari frekuensi kesulitan tidur
    adjustment = KESULITAN_ADJUSTMENT_MAP.get(kesulitan_tidur, 0.0)
    insomnia_score = float(np.clip(prob_insomnia + adjustment, 0, 100))
    insomnia_label = _insomnia_category(insomnia_score)

    # --- Model 2: Produktivitas (sleep, phone, coffee, exercise, stress) ---
    phone_usage_hours = PHONE_USAGE_MAP.get(layar_sebelum_tidur, 1.0)
    coffee_intake_mg = COFFEE_INTAKE_MAP.get(konsumsi_kafein, 100)
    x2 = [durasi_tidur, phone_usage_hours, coffee_intake_mg, aktivitas_fisik, tingkat_stres]

    x2_scaled = productivity_scaler.transform([x2])
    prod_idx = int(productivity_model.predict(x2_scaled)[0])
    prod_label = PRODUCTIVITY_LABELS[prod_idx]
    prod_confidence = float(np.max(productivity_model.predict_proba(x2_scaled)[0]) * 100)

    analisis = _build_analysis(
        durasi_tidur, kualitas_tidur, aktivitas_fisik, layar_sebelum_tidur,
        konsumsi_kafein, kesulitan_tidur, insomnia_label, prod_label,
    )

    return {
        "produktivitas_label": prod_label,
        "produktivitas_confidence": round(prod_confidence, 2),
        "insomnia_label": insomnia_label,
        "insomnia_confidence": round(insomnia_score, 2),
        "analisis_terpadu": analisis,
    }

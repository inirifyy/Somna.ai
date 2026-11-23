# backend/prediction.py
# Tugas file ini: menjalankan 2 model JST + hybrid scoring dan menyusun hasil
# untuk result.html.
#
# Logika (mapping, clip, hybrid scoring, kategori, analisis terpadu) = versi Aidil,
# TIDAK diubah. Satu-satunya tambahan: model dimuat saat pertama kali dibutuhkan
# (bukan saat import), supaya aplikasi tidak langsung mati kalau file model
# belum ada / rusak. Kalau model ada, hasilnya sama persis dengan versi aslinya.

import os

import joblib
import numpy as np

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_DIR = os.path.join(BASE_DIR, "models")

# Cache: model cukup dimuat sekali, bukan setiap ada request.
_cache = {}


def _muat(nama):
    """Memuat model + scaler ('sleep' atau 'productivity'). Mengembalikan dict."""
    if nama not in _cache:
        try:
            _cache[nama] = {
                "model": joblib.load(os.path.join(MODEL_DIR, f"{nama}_model.keras")),
                "scaler": joblib.load(os.path.join(MODEL_DIR, f"{nama}_scaler.pkl")),
            }
        except Exception as e:
            _cache[nama] = {"error": f"{type(e).__name__}: {e}"}
    return _cache[nama]


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

BELUM_TERSEDIA = "Belum tersedia"


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

    if insomnia_label and prod_label:
        head = f"Produktivitas terprediksi {prod_label}, indikasi insomnia: {insomnia_label}."
    else:
        head = "Prediksi model belum tersedia, berikut analisis berdasarkan jawabanmu."

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

    insomnia_label, insomnia_score = None, None
    prod_label, prod_confidence = None, None
    pesan_model = []

    # --- Model 1: Insomnia (Sleep Duration, Quality, Physical Activity, Stress) ---
    sleep = _muat("sleep")
    if "error" in sleep:
        pesan_model.append(f"Model insomnia belum bisa dimuat ({sleep['error']})")
    else:
        x1 = _clip([durasi_tidur, kualitas_tidur, aktivitas_fisik, tingkat_stres], SLEEP_FEATURE_BOUNDS)
        prob_insomnia = sleep["model"].predict_proba(sleep["scaler"].transform([x1]))[0][1] * 100

        # Hybrid Scoring (PRD §4.C): tambah adjustment dari frekuensi kesulitan tidur
        adjustment = KESULITAN_ADJUSTMENT_MAP.get(kesulitan_tidur, 0.0)
        insomnia_score = float(np.clip(prob_insomnia + adjustment, 0, 100))
        insomnia_label = _insomnia_category(insomnia_score)

    # --- Model 2: Produktivitas (sleep, phone, coffee, exercise, stress) ---
    prod = _muat("productivity")
    if "error" in prod:
        pesan_model.append(f"Model produktivitas belum bisa dimuat ({prod['error']})")
    else:
        phone_usage_hours = PHONE_USAGE_MAP.get(layar_sebelum_tidur, 1.0)
        coffee_intake_mg = COFFEE_INTAKE_MAP.get(konsumsi_kafein, 100)
        x2 = [durasi_tidur, phone_usage_hours, coffee_intake_mg, aktivitas_fisik, tingkat_stres]

        x2_scaled = prod["scaler"].transform([x2])
        prod_idx = int(prod["model"].predict(x2_scaled)[0])
        prod_label = PRODUCTIVITY_LABELS[prod_idx]
        prod_confidence = float(np.max(prod["model"].predict_proba(x2_scaled)[0]) * 100)

    analisis = _build_analysis(
        durasi_tidur, kualitas_tidur, aktivitas_fisik, layar_sebelum_tidur,
        konsumsi_kafein, kesulitan_tidur, insomnia_label, prod_label,
    )

    hasil = {
        "produktivitas_label": prod_label or BELUM_TERSEDIA,
        "produktivitas_confidence": round(prod_confidence, 2) if prod_label else None,
        "insomnia_label": insomnia_label or BELUM_TERSEDIA,
        "insomnia_confidence": round(insomnia_score, 2) if insomnia_label else None,
        "analisis_terpadu": analisis,
    }
    if pesan_model:                      # hanya muncul kalau ada model yang gagal dimuat
        hasil["pesan_model"] = pesan_model
    return hasil
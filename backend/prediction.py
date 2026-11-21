# backend/prediction.py
# Tugas file ini: memuat model + scaler + label, lalu menjalankan prediksi.
# Kalau file model belum ada / masih kosong, aplikasi TIDAK crash:
# hasilnya ditandai "tersedia": False dan sisanya (rule-based) tetap jalan.

import bisect
import json
from pathlib import Path

import joblib

MODELS_DIR = Path(__file__).resolve().parent.parent / "models"

# Cache: model cukup dimuat sekali, bukan setiap ada request.
_cache = {}


def _file_siap(path):
    """File harus ada DAN tidak kosong (file di ZIP awal berukuran 0 byte)."""
    return path.exists() and path.stat().st_size > 0


def _muat(nama):
    """Memuat paket (model, scaler, label) untuk 'productivity' atau 'sleep'."""
    if nama in _cache:
        return _cache[nama]

    path_model = MODELS_DIR / f"{nama}_model.keras"
    path_scaler = MODELS_DIR / f"{nama}_scaler.pkl"
    path_label = MODELS_DIR / f"{nama}_labels.json"

    if not all(_file_siap(p) for p in (path_model, path_scaler, path_label)):
        _cache[nama] = {"error": "File model belum tersedia."}
        return _cache[nama]

    try:
        # TensorFlow diimpor di sini (bukan di atas) supaya server tetap
        # bisa menyala walaupun TensorFlow bermasalah.
        from tensorflow import keras

        _cache[nama] = {
            "model": keras.models.load_model(path_model),
            "scaler": joblib.load(path_scaler),
            "label": json.loads(path_label.read_text(encoding="utf-8")),
        }
    except Exception as e:
        _cache[nama] = {"error": f"Model gagal dimuat: {e}"}

    return _cache[nama]


def _kategori(nilai, batas, nama_kelas):
    """
    Menentukan kelas berdasarkan batas.
    Contoh: batas=[40, 60], kelas=[Rendah, Sedang, Tinggi]
      nilai 35 -> Rendah, nilai 50 -> Sedang, nilai 75 -> Tinggi
    """
    return nama_kelas[bisect.bisect_right(batas, nilai)]


def _jalankan(nama, x):
    """Scaler -> model -> satu angka keluaran. Mengembalikan (angka, label) atau (None, error)."""
    paket = _muat(nama)
    if "error" in paket:
        return None, paket

    x_scaled = paket["scaler"].transform(x)            # scaler yang SAMA dengan training
    keluaran = paket["model"].predict(x_scaled, verbose=0)
    return float(keluaran[0][0]), paket["label"]


def prediksi_produktivitas(x):
    """Model regresi: keluaran = skor produktivitas, lalu dikelompokkan jadi 3 kelas."""
    skor, label = _jalankan("productivity", x)
    if skor is None:
        return {"tersedia": False, "pesan": label["error"]}

    skor = max(0.0, min(100.0, skor))                  # skor dibatasi 0-100
    return {
        "tersedia": True,
        "skor": round(skor, 1),
        "kategori": _kategori(skor, label["thresholds"], label["labels"]),
    }


def prediksi_insomnia(x):
    """Model biner: keluaran = peluang pola mirip kelas Insomnia (0-1), bukan diagnosis."""
    peluang, label = _jalankan("sleep", x)
    if peluang is None:
        return {"tersedia": False, "pesan": label["error"]}

    return {
        "tersedia": True,
        "peluang": round(peluang, 3),
        "kategori": _kategori(peluang, label["thresholds"], label["labels"]),
    }


def prediksi_semua(fitur):
    """Pintu masuk utama: menerima hasil siapkan_fitur(), mengembalikan dua hasil."""
    return {
        "produktivitas": prediksi_produktivitas(fitur["productivity"]),
        "insomnia": prediksi_insomnia(fitur["sleep"]),
    }
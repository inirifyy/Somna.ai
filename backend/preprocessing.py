# backend/preprocessing.py
# Tugas file ini: mengubah input pengguna yang sudah valid menjadi susunan angka
# yang SAMA PERSIS dengan yang dipakai saat training (urutan kolom & skala).
# Scaling (StandardScaler) dilakukan di prediction.py, karena scaler
# adalah pasangan dari model-nya.

import numpy as np

# ---------------------------------------------------------------------------
# URUTAN FITUR MODEL  (HARUS sama dengan urutan kolom saat training!)
# ---------------------------------------------------------------------------
# Model insomnia (Sleep Health): Sleep Duration, Quality of Sleep,
# Physical Activity Level, Stress Level
SLEEP_FEATURES = ["sleep_duration", "sleep_quality", "physical_activity", "stress_level"]

# Model produktivitas: PLACEHOLDER. Ubah setelah Aidil memutuskan fitur finalnya
# (lihat diskusi soal study_hours). Urutan harus sama dengan notebook training.
PRODUCTIVITY_FEATURES = ["sleep_duration", "stress_level"]


def skala_5_ke_10(nilai):
    """
    Mengubah skala form 1-5 menjadi skala 1-10 secara linear:
    1 -> 1, 3 -> 5.5, 5 -> 10.
    (SEMENTARA - rumus konversi harus disepakati kelompok.)
    """
    return 1 + (nilai - 1) * 9 / 4


def konversi_fitur(data):
    """Dari input form (skala form) menjadi nilai berskala dataset."""
    return {
        "sleep_duration": data["sleep_duration"],                    # jam, sama
        "sleep_quality": skala_5_ke_10(data["sleep_quality"]),       # 1-5 -> 1-10
        "physical_activity": data["physical_activity"],              # menit/hari
        "stress_level": skala_5_ke_10(data["stress_level"]),         # 1-5 -> 1-10
    }


def susun_vektor(fitur, urutan):
    """Menyusun dict menjadi array 2 dimensi (1 baris) sesuai urutan kolom."""
    return np.array([[fitur[nama] for nama in urutan]], dtype=float)


def siapkan_fitur(data):
    """
    Pintu masuk utama file ini.
    Mengembalikan dua array: satu untuk model insomnia, satu untuk produktivitas.
    """
    fitur = konversi_fitur(data)
    return {
        "sleep": susun_vektor(fitur, SLEEP_FEATURES),
        "productivity": susun_vektor(fitur, PRODUCTIVITY_FEATURES),
    }
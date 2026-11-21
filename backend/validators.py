# backend/validators.py
# Tugas file ini: memeriksa data dari form SEBELUM dipakai model.
# Kita tidak boleh percaya data dari pengguna, karena validasi di JavaScript
# bisa dilewati. Jadi backend wajib memeriksa ulang.

import math

# ---------------------------------------------------------------------------
# TABEL ATURAN INPUT  (SEMENTARA - skala belum disepakati kelompok)
# Kunci ("sleep_difficulty", dst.) = atribut name di HTML form milik Inri.
# Kalau kelompok mengubah skala, cukup ubah tabel ini.
# ---------------------------------------------------------------------------
FIELD_SPECS = {
    "sleep_difficulty": {"label": "Kesulitan tidur malam",       "tipe": "int",   "min": 1,   "max": 5},
    "sleep_duration":   {"label": "Durasi tidur (jam)",          "tipe": "float", "min": 2,   "max": 12},
    "sleep_quality":    {"label": "Kualitas tidur",              "tipe": "int",   "min": 1,   "max": 5},
    "phone_before_bed": {"label": "Ponsel sebelum tidur",        "tipe": "int",   "min": 1,   "max": 5},
    "caffeine_freq":    {"label": "Frekuensi konsumsi kafein",   "tipe": "int",   "min": 1,   "max": 5},
    "physical_activity": {"label": "Aktivitas fisik (menit/hari)", "tipe": "int", "min": 0,   "max": 240},
    "stress_level":     {"label": "Tingkat stres",               "tipe": "int",   "min": 1,   "max": 5},
}


def _ubah_ke_angka(teks, tipe):
    """Ubah teks dari form menjadi angka. Mengembalikan None kalau gagal."""
    teks = teks.replace(",", ".")  # orang Indonesia sering mengetik 7,5

    try:
        nilai = float(teks)
    except ValueError:
        return None

    # float("nan") dan float("inf") lolos float(), tapi bukan angka yang wajar
    if not math.isfinite(nilai):
        return None

    if tipe == "int":
        if nilai != int(nilai):   # "3.5" tidak boleh untuk kolom bilangan bulat
            return None
        return int(nilai)

    return nilai


def validate_input(form):
    """
    Memeriksa semua input.

    Parameter:
        form : data dari form, bisa request.form (Flask) atau dict biasa.

    Mengembalikan dua hal:
        data   : dict berisi angka yang sudah bersih (hanya valid jika errors kosong)
        errors : dict berisi pesan kesalahan per field (kosong = semua valid)
    """
    data = {}
    errors = {}

    for nama, aturan in FIELD_SPECS.items():
        teks = str(form.get(nama, "")).strip()
        label = aturan["label"]

        # 1. Kosong?
        if teks == "":
            errors[nama] = f"{label} wajib diisi."
            continue

        # 2. Bisa jadi angka (dan bilangan bulat kalau wajib)?
        nilai = _ubah_ke_angka(teks, aturan["tipe"])
        if nilai is None:
            if aturan["tipe"] == "int":
                errors[nama] = f"{label} harus berupa bilangan bulat."
            else:
                errors[nama] = f"{label} harus berupa angka."
            continue

        # 3. Di dalam rentang?
        if nilai < aturan["min"] or nilai > aturan["max"]:
            errors[nama] = (f"{label} harus antara "
                            f"{aturan['min']} dan {aturan['max']}.")
            continue

        data[nama] = nilai

    return data, errors
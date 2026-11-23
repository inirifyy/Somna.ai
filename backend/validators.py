# backend/validators.py
# Tugas file ini: memeriksa data dari form SEBELUM dipakai model.
# Kita tidak boleh percaya data dari pengguna, karena validasi di JavaScript
# bisa dilewati. Jadi backend wajib memeriksa ulang.

import math

FREKUENSI = ["Tidak", "Jarang", "Sering", "Selalu"]

# ---------------------------------------------------------------------------
# TABEL ATURAN INPUT
# Kunci = atribut name di HTML form (harus sama persis dengan milik Inri).
# tipe "pilihan" = harus salah satu dari daftar "opsi".
# ---------------------------------------------------------------------------
FIELD_SPECS = {
    "durasi_tidur":        {"label": "Durasi tidur (jam)",         "tipe": "float",   "min": 2, "max": 12},
    "kualitas_tidur":      {"label": "Kualitas tidur",             "tipe": "int",     "min": 1, "max": 10},
    "aktivitas_fisik":     {"label": "Aktivitas fisik (menit)",    "tipe": "int",     "min": 0, "max": 240},
    "tingkat_stres":       {"label": "Tingkat stres",              "tipe": "int",     "min": 1, "max": 10},
    "layar_sebelum_tidur": {"label": "Layar sebelum tidur",        "tipe": "pilihan", "opsi": FREKUENSI},
    "konsumsi_kafein":     {"label": "Konsumsi kafein",            "tipe": "pilihan", "opsi": FREKUENSI},
    "kesulitan_tidur":     {"label": "Kesulitan tidur malam",      "tipe": "pilihan", "opsi": FREKUENSI},
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

    Mengembalikan dua hal:
        data   : dict nilai yang sudah bersih (valid hanya jika errors kosong)
        errors : dict pesan kesalahan per field (kosong = semua valid)
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

        # 2a. Pilihan teks: harus salah satu opsi
        if aturan["tipe"] == "pilihan":
            if teks not in aturan["opsi"]:
                errors[nama] = f"{label} harus salah satu dari: {', '.join(aturan['opsi'])}."
                continue
            data[nama] = teks
            continue

        # 2b. Angka: bisa diubah, dan bilangan bulat kalau wajib?
        nilai = _ubah_ke_angka(teks, aturan["tipe"])
        if nilai is None:
            if aturan["tipe"] == "int":
                errors[nama] = f"{label} harus berupa bilangan bulat."
            else:
                errors[nama] = f"{label} harus berupa angka."
            continue

        # 3. Di dalam rentang?
        if nilai < aturan["min"] or nilai > aturan["max"]:
            errors[nama] = f"{label} harus antara {aturan['min']} dan {aturan['max']}."
            continue

        data[nama] = nilai

    return data, errors
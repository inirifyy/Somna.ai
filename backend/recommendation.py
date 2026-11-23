# backend/recommendation.py
# Tugas file ini: rule-based engine (aturan if-else) yang menyusun analisis dan
# rekomendasi dari input pengguna + hasil prediksi.
# Semua ambang batas di bawah adalah USULAN dan perlu dicocokkan dengan sumber
# yang bisa dikutip kelompok (tandai di dokumentasi).

DISCLAIMER = (
    "Hasil ini adalah skrining awal berbasis model statistik, bukan diagnosis medis. "
    "Jika keluhan tidur berlangsung lama atau mengganggu aktivitas, "
    "konsultasikan dengan tenaga kesehatan profesional."
)


def _analisis_tidur(data):
    catatan = []
    rekomendasi = []

    durasi = data["sleep_duration"]
    if durasi < 6:
        catatan.append(f"Durasi tidurmu {durasi} jam, tergolong kurang.")
        rekomendasi.append("Majukan jam tidur secara bertahap, misalnya 15 menit lebih awal setiap hari.")
    elif durasi < 7:
        catatan.append(f"Durasi tidurmu {durasi} jam, sedikit di bawah rentang yang umum disarankan (7-9 jam).")
        rekomendasi.append("Usahakan mendekati 7-9 jam tidur per malam.")
    elif durasi <= 9:
        catatan.append(f"Durasi tidurmu {durasi} jam, berada di rentang yang umum disarankan.")
    else:
        catatan.append(f"Durasi tidurmu {durasi} jam, cukup panjang.")
        rekomendasi.append("Jika tetap lelah walau tidur panjang, perhatikan kualitas tidurmu.")

    if data["sleep_quality"] <= 2:
        catatan.append("Kualitas tidurmu dinilai rendah.")
        rekomendasi.append("Jaga kamar tetap gelap, tenang, dan sejuk, serta tidur di jam yang konsisten.")

    if data["sleep_difficulty"] >= 4:
        catatan.append("Kamu cukup sering mengalami kesulitan tidur di malam hari.")
        rekomendasi.append("Buat rutinitas santai sebelum tidur. Jika berlangsung berminggu-minggu, "
                           "pertimbangkan berkonsultasi dengan tenaga kesehatan.")

    return catatan, rekomendasi


def _analisis_ponsel(data):
    nilai = data["phone_before_bed"]
    if nilai >= 4:
        return (["Penggunaan ponsel sebelum tidurmu tergolong sering."],
                ["Letakkan ponsel di luar jangkauan saat waktu tidur atau aktifkan mode fokus."])
    if nilai == 3:
        return (["Penggunaan ponsel sebelum tidurmu tergolong sedang."],
                ["Coba batasi layar secara bertahap sebelum tidur."])
    return (["Kebiasaan ponsel sebelum tidurmu tergolong terkendali."], [])


def _analisis_aktivitas(data):
    menit = data["physical_activity"]
    if menit < 20:
        return ([f"Aktivitas fisikmu {menit} menit per hari, tergolong rendah."],
                ["Mulai dari jalan santai 10-15 menit per hari lalu tingkatkan perlahan."])
    if menit < 45:
        return ([f"Aktivitas fisikmu {menit} menit per hari, cukup."],
                ["Pertahankan, dan tambah bertahap bila memungkinkan."])
    return ([f"Aktivitas fisikmu {menit} menit per hari, tergolong baik."], [])


def _analisis_gaya_hidup(data):
    catatan, rekomendasi = [], []
    if data["caffeine_freq"] >= 4:
        catatan.append("Konsumsi kafeinmu tergolong sering.")
        rekomendasi.append("Kurangi kafein di sore dan malam hari.")
    if data["stress_level"] >= 4:
        catatan.append("Tingkat stresmu tergolong tinggi.")
        rekomendasi.append("Coba latihan napas atau menulis jurnal singkat sebelum tidur.")
    return catatan, rekomendasi


def _penjelasan(prediksi):
    kalimat = []
    prod = prediksi["produktivitas"]
    ins = prediksi["insomnia"]

    if prod["tersedia"]:
        kalimat.append(f"Perkiraan tingkat produktivitasmu: {prod['kategori']} (skor {prod['skor']}).")
    else:
        kalimat.append("Prediksi produktivitas belum tersedia.")

    if ins["tersedia"]:
        kalimat.append(
            f"Pola kebiasaanmu memiliki kemiripan dengan pola insomnia pada data pelatihan: "
            f"{ins['kategori']}. Ini bukan diagnosis dan bukan ukuran keparahan klinis."
        )
    else:
        kalimat.append("Skrining insomnia belum tersedia.")

    return " ".join(kalimat)


def buat_rekomendasi(data, prediksi):
    """Pintu masuk utama. Mengembalikan dict yang langsung bisa dipakai result.html."""
    hasil = {}
    semua_saran = []

    for kunci, fungsi in [
        ("analisis_tidur", _analisis_tidur),
        ("analisis_ponsel", _analisis_ponsel),
        ("analisis_aktivitas", _analisis_aktivitas),
        ("analisis_gaya_hidup", _analisis_gaya_hidup),
    ]:
        catatan, saran = fungsi(data)
        hasil[kunci] = catatan
        semua_saran.extend(saran)

    hasil["rekomendasi"] = semua_saran or ["Kebiasaanmu sudah cukup baik, pertahankan."]
    hasil["penjelasan"] = _penjelasan(prediksi)
    hasil["disclaimer"] = DISCLAIMER
    return hasil